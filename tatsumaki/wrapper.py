import aiohttp
from ratelimit import limits
from typing import Union

import data_structures as ds


class ApiWrapper:
    def __init__(self, key):
        self.key = key
        self.base_url = "https://api.tatsu.gg/v1/"
        self.headers = {"Authorization": key}

    @limits(calls=60, period=60)
    async def request(self, url):
        """Directly interact with the API to get the unfiltered results."""
        async with aiohttp.ClientSession() as session:
            async with session.get(url=self.base_url + url, headers=self.headers) as result:
                if result.status != 200:
                    return result.raise_for_status()
                return await result.json()

    async def get_profile(self, user_id: int) -> Union[Exception, ds.UserProfile]:
        """Gets a user's profile. Returns a user object on success."""
        try:
            result = await self.request(f"users/{user_id}/profile")
        except Exception as e:
            return e
        user = ds.UserProfile(
            avatar_url=result.get('avatar_url', None),
            credits_=result.get('credits', None),
            discriminator=result.get('discriminator', None),
            id_=result.get('id', None),
            info_box=result.get('info_box', None),
            reputation=result.get('reputation', None),
            title=result.get('title', None),
            tokens=result.get('tokens', None),
            username=result.get('username', None),
            xp=result.get('xp', None),
        )
        return user

    async def get_member_ranking(self, guild_id: int, user_id: int) -> Union[ds.Ranking, Exception]:
        """Gets the all-time ranking for a guild member. Returns a guild member ranking object on success."""
        try:
            result = await self.request(f"/guilds/{guild_id}/rankings/members/{user_id}/all")
        except Exception as e:
            return e
        rank = self.ranking_object(result)
        return rank

    @staticmethod
    def ranking_object(result) -> ds.Ranking:
        """Initiate the rank profile"""
        rank = ds.Ranking(
            guild_id=result.get('guild_id', None),
            rank=result.get('rank', None),
            score=result.get('score', None),
            user_id=result.get('user_id', None)
        )
        return rank

    async def get_guild_rankings(self, guild_id, offset=0) -> Union[ds.GuildRankings, Exception]:
        """Gets all-time rankings for a guild. Returns a guild rankings object on success."""
        try:
            result = await self.request(f"/guilds/{guild_id}/rankings/all?offset={offset}")
        except Exception as e:
            return e
        rankings = ds.GuildRankings(
            guild_id=result.get('guild_id', None),
            rankings=[self.ranking_object(i) for i in result.get('rankings', [{}])]
        )
        return rankings


if __name__ == '__main__':
    import asyncio
    loop = asyncio.get_event_loop()

    async def main():
        wrapper = ApiWrapper("ArQf6QFoCR-sElZOduZhvJtwUJ7XwZkS7")
        # print(await wrapper.get_profile(274561812664549376))
        # print(await wrapper.get_member_ranking(573885009820254239, 274561812664549376))
        rankings = await wrapper.get_guild_rankings(573885009820254239)
        print(rankings.rankings[0].user_id)
    loop.run_until_complete(main())