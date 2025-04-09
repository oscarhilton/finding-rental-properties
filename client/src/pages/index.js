import Head from 'next/head';

import Layout from '@components/Layout';
import Section from '@components/Section';
import Container from '@components/Container';
import Map from '@components/Map';
import Button from '@components/Button';

import styles from '@styles/Home.module.scss';

import fs from "fs";
import path from "path";
import { useState } from 'react';

const DEFAULT_CENTER = [51.5074, -0.1278]; // London Coordinates

function processLineStrings(lineStrings) {
  if (!lineStrings) return []
  return lineStrings.map(lineString => {
    // Parse the string to get an array of coordinates
    const coordinates = JSON.parse(lineString);
    
    // Reverse the coordinates from [lng, lat] to [lat, lng]
    return coordinates.map(pair => pair.map(([lng, lat]) => [lat, lng]));
  });
}

export async function getStaticProps() {
  // Path to the compiled JSON file
  const filePath = path.join(process.cwd(), "public", "data", "compiled.json");

  // Read the JSON file
  const fileContents = fs.readFileSync(filePath, "utf8");

  // Parse the file contents into an array
  const jsonData = JSON.parse(fileContents);

  // Return the data as props to the page
  return {
    props: {
      data: jsonData,
    },
  };
}

export default function Home({ data, json }) {
  // const [startQuery, setStartQuery] = useState('');
  // const [endQuery, setEndQuery] = useState('');
  const [loading, setLoading] = useState(false);

  const [start, setStart] = useState(null);
  const [end, setEnd] = useState(null);

  const [startDisplayName, setStartDisplayName] = useState('');
  const [endDisplayName, setEndDisplayName] = useState('');

  const [route, setRoute] = useState([]);

  const getRoute = async () => {
    setLoading(true);
    try {
      const route = await fetch(`http://localhost:3000/api/route`, {
        headers: {'Content-Type': 'application/json'},
        method: "POST",
        body: JSON.stringify({
          orig: start,
          dest: end
        })
      });
      json = await route.json();
      setRoute(json.route)
    } catch (e) {

    } finally {
      setLoading(false);
    }
  }

  const getAddressFromQuery = async (searchTerm, callback) => {
    if (!searchTerm || searchTerm.length < 3) return
    setLoading(true);
    try {
      const request = await fetch(`https://nominatim.openstreetmap.org/search?q=${searchTerm}&format=json&addressdetails=1&limit=1&polygon_svg=1`)
      const json = await request.json();
      const firstResult = json[0];
      callback(firstResult)
    } catch (e) {
      console.log(e);
    } finally {
      setLoading(false);
    }
  }

  return (
    <Layout>
      <Head>
        <title>Next.js Leaflet Starter</title>
        <meta name="description" content="Create mapping apps with Next.js Leaflet Starter" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <Section>
        <Container>
          <div>
            <Button onClick={getRoute}>Click me</Button>
          </div>
          <div>
            <Button onClick={() => getAddressFromQuery("TW2 6JA", (result) => {
              setStartDisplayName(result.display_name)
              setStart([result.lat, result.lon])
            })}>Get TW2 6JA</Button>
          </div>
          <div>
            <Button onClick={() => getAddressFromQuery("Southall", (result) => {
              setEndDisplayName(result.display_name)
              setEnd([result.lat, result.lon])
            })}>Get Southall</Button>
          </div>
          {!!startDisplayName && (
            <div>
              <h2>Start</h2>
              <h4>{startDisplayName}</h4>
              <h2>End</h2>
              <h4>{endDisplayName}</h4>
            </div>
          )}
          <Map className={styles.homeMap} width="1280" height="800" center={start ? start : [51.448538, -0.355183]} zoom={12}>
            {({ TileLayer, Marker, Popup, Polyline, Circle }) => (
              <>
                <TileLayer
                  url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
                  attribution="&copy; <a href=&quot;http://osm.org/copyright&quot;>OpenStreetMap</a> contributors"
                />
                <Polyline positions={route && route} color="black" />
                {!!start && (
                  <Marker position={start} /> 
                )}
                {!!end && (
                  <Marker position={start} /> 
                )}
                {!data && data.map(({ lineStrings, hex, sequences }) => (
                    <>
                      <Polyline positions={processLineStrings(lineStrings)} color={hex} />
                      {sequences && sequences.map(({ sequences }) => (
                        <>
                          {sequences && sequences.map(({ lat, lon }) => (
                            <Circle
                              attribution="test"
                              center={[lat, lon]}
                              radius={10}
                              pathOptions={{ 
                                color: 'white',
                                fill: true,
                                fillColor: '#f5f5f5',
                                fillOpacity: 1,
                              }}
                            />
                          ))}
                        </>
                      ))}
                    </>
                ))}
                <Marker position={DEFAULT_CENTER}>
                  <Popup>
                    Welcome to London! <br /> This is your map with coordinates.
                  </Popup>
                </Marker>
              </>
            )}
          </Map>
        </Container>
        {/* <pre>{JSON.stringify(data, null, 2)}</pre> */}
      </Section>
    </Layout>
  )
}
