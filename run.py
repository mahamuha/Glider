import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.__init__:app", reload=True)

