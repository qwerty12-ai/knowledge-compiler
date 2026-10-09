import asyncio

from backend.app.worker import create_analysis_worker

async def main():
	worker = await create_analysis_worker()

	try:
		await asyncio.Event().wait()
	finally:
		await worker.close()

if __name__ == "__main__":
	asyncio.run(main())
