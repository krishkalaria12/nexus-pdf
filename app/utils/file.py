import os
import aiofiles

async def save_file(file: bytes, file_path: str):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    async with aiofiles.open(file_path, 'wb') as out_file:
        await out_file.write(file)

    return True