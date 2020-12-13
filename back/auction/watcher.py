import asyncio
from datetime import datetime

from sqlalchemy import and_

from ..db_utils import db
from ..settings import DB_DSN
from ..user.models import UserModel
from .models import AuctionModel, BetModel
from .views import fake_send_mail, fake_send_tg_sentry


async def watch_task():
    async with db.with_bind(bind=DB_DSN):
        while True:
            try:
                auctions = await AuctionModel.load(
                    owner=UserModel.on(AuctionModel.owner == UserModel.id)
                ).query.where(and_(AuctionModel.end <= datetime.utcnow(), AuctionModel.is_active == True)).gino.all()

                if auctions:
                    bets = await BetModel.load(
                        user=UserModel.on(BetModel.user == UserModel.id),
                        auction=AuctionModel.on(BetModel.auction == AuctionModel.id)
                    ).query.where(
                        BetModel.auction.in_([auction.id for auction in auctions])
                    ).order_by(
                        BetModel.price.desc()
                    ).gino.all()

                    for i, bet in enumerate(bets):
                        auction_status = "won" if i == 0 else "lost"
                        await fake_send_mail(f"Auction {bet.auction.name}({bet.auction.id}) is closed",
                                             f"You {auction_status}", [bet.user.email])

                    for auction in auctions:
                        await auction.update(is_active=False).apply()
            except Exception as e:
                await fake_send_tg_sentry(str(e))

            await asyncio.sleep(10000)


def watch_auction():
    print('### STARTED WATCHING ###')
    loop = asyncio.get_running_loop()
    loop.create_task(watch_task())
