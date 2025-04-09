// Next.js API route support: https://nextjs.org/docs/api-routes/introduction

export default async (req, res) => {
    try {

        const {orig, dest} = req.body;

        const payload = JSON.stringify({
            orig,
            dest
        })

        const route = await fetch("http://127.0.0.1:8000/route", {
            headers: {'Content-Type': 'application/json'},
            method: "POST",
            body: payload
        });

        const json = await route.json();
        
        res.statusCode = 200
        res.json(json)
    } catch(e) {
        console.log(e)
        res.statusCode = 500
    }
  }
  