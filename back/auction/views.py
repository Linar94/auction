from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status, APIRouter

from ..auth.depends import get_user
from ..user.dataclasses import User
from ..user.models import UserModel
from .models import AuctionModel, BetModel
from .dataclasses import AuctionListParams, AuctionCreateParams, BetCreateParams, AuctionDetailParams


router = APIRouter()


async def fake_send_mail(subject: str, body: str, recipients: list) -> bool:
    return True


async def fake_send_tg_sentry(trace: str) -> bool:
    return True


@router.get("/auction/list")
async def get_auction_list(params: AuctionListParams, user: User = Depends(get_user)):
    auctions = AuctionModel.query
    if params.state == 'active':
        auctions = auctions.where(AuctionModel.is_active.is_(True))
    elif params.state == 'inactive':
        auctions = auctions.where(AuctionModel.is_active.is_(False))

    auctions = await auctions.gino.all()

    return [{"id": auction.id, "name": auction.name, "created": auction.created} for auction in auctions]


@router.post("/auction/create")
async def create_auction(params: AuctionCreateParams, user: User = Depends(get_user)):
    if await AuctionModel.query.where(AuctionModel.name == params.name).gino.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Auction with name {params.name} already exists",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        auction = await AuctionModel.create(price=params.price,
                                            steps=params.step,
                                            created=datetime.utcnow(),
                                            end=params.end_dt,
                                            name=params.name,
                                            owner=user.id,
                                            is_active=True)
    except Exception as e:
        await fake_send_tg_sentry(str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="",
            headers={"WWW-Authenticate": "Bearer"},
        )
    else:
        for user_ in await UserModel.query.where(UserModel.id != user.id).gino.all():
            await fake_send_mail(f"Join to auction {auction.id}", ".", [user_.email])

    return {"created": True, "auction": auction.id}


@router.post("/bet/create")
async def create_bet(params: BetCreateParams, user: User = Depends(get_user)):
    auction = await AuctionModel.query.where(AuctionModel.id == params.auction).gino.first()
    dt_created = datetime.utcnow()

    if not auction:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Auction is not exist",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not auction.is_active or dt_created > auction.end:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Auction already have been closed",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.id == auction.owner:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Owner can't create bet",
            headers={"WWW-Authenticate": "Bearer"},
        )

    bets = await BetModel.load(
        user=UserModel.on(BetModel.user == UserModel.id)
    ).query.where(
        BetModel.auction == auction.id
    ).order_by(
        BetModel.created.desc()
    ).gino.all()

    if params.price <= auction.price or (bets and params.price <= bets[0].price):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Price is less than action start price/last bet price",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if ((params.price - auction.price) % auction.steps) != 0 or (bets and params.price <= bets[0].price):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wrong step",
            headers={"WWW-Authenticate": "Bearer"},
        )

    bet = await BetModel.create(price=params.price, user=user.id, auction=auction.id, created=dt_created)
    for bet in bets:
        await fake_send_mail(f"Last bet increased at {dt_created}", f"Action ID - {auction.id}\nYour last price - {bet.price}\nNew price - {params.price}",
                             [bet.user.email])

    return {"created": True, "bet": bet.id}


@router.get("/auction/detail")
async def get_auction_detail(params: AuctionDetailParams, user: User = Depends(get_user)):
    auction = await AuctionModel.load(
        owner=UserModel.on(AuctionModel.owner == UserModel.id)
    ).query.where(
        AuctionModel.id == params.auction
    ).gino.first()

    if not auction:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Auction doesn't exist",
            headers={"WWW-Authenticate": "Bearer"},
        )

    auction_detail_result = {
        "id": auction.id,
        "name": auction.name,
        "owner": auction.owner.username,
        "price": auction.price,
        "step": auction.steps,
        "created": auction.created,
        "end": auction.end
    }

    bets = await BetModel.load(
        user=UserModel.on(BetModel.user == UserModel.id)
    ).query.where(
        BetModel.auction == params.auction
    ).order_by(
        BetModel.created.desc()
    ).gino.all()

    auction_detail_result["bets"] = [{"price": bet.price, "user_name": bet.user.username,
                                      "user_id": bet.user.id} for bet in bets]

    return auction_detail_result

