from database import async_session


async def get_async_session():
    try:
        new_session = async_session()

        yield new_session

    except:
        await new_session.rollback()
        raise

    finally:
        await new_session.close()
