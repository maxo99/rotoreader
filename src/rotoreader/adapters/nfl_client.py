# from collections.abc import Sequence

# import nfl_data_py as nfl

# DATA_DIR = "./data/"


# def preload_pbp(years: Sequence[int]):
#     nfl.cache_pbp(years, downcast=True, alt_path=DATA_DIR)


# # def get_pbp(years: Sequence[int] | int):
# #     if isinstance(years, int):
# #         years = [years]
# #     try:
# #         return nfl.import_pbp_data(
# #             years,
# #             downcast=True,
# #             cache=True,
# #             alt_path=DATA_DIR,
# #         )
# #     except ValueError:
# #         preload_pbp(years)
# #         return nfl.import_pbp_data(
# #             years,
# #             downcast=True,
# #             cache=True,
# #             alt_path=DATA_DIR,
# #         )
