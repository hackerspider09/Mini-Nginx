import asyncio

async def fn():
	
	print("one")
	await asyncio.sleep(5)
	await fn2()
	print('four')
	await asyncio.sleep(5)
	print('five')
	await asyncio.sleep(5)

async def fn2():
	await asyncio.sleep(5)
	print("two")
	await asyncio.sleep(5)
	print("three")
asyncio.run(fn())
