// Next.js API route support: https://nextjs.org/docs/api-routes/introduction

export default async (req, res) => {
    const startLatlon = [51.450931,-0.357921]
    const endLatlon = [51.445235, -0.325506]

    try {
        const payload = JSON.stringify({
            orig: startLatlon,
            dest: endLatlon
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
  