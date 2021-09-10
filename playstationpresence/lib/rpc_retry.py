def rpc_retry(func):
    def wrapper(*args):
        try:
            func(*args)
        except Exception as e:
            print("Discord RPC error")
            print(e)

            # Seems like the RPC connection can go stale or some such
            # Create a new instance on failure and retry once
            instance = args[0]
            instance.initRpc()

            try:
                func(*args)
            except Exception as e:
                print("Discord RPC error on retry")
                print(e)

                instance.quit()
    
    return wrapper