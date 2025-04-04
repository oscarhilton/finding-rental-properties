// Next.js API route support: https://nextjs.org/docs/api-routes/introduction

export default async (req, res) => {
    const route = await fetch("http://127.0.0.1:8000/route");
    const json = await route.json();
    console.log(route);
    res.statusCode = 200
    res.json(json)
  }
  