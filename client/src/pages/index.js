import Head from 'next/head';

import Layout from '@components/Layout';
import Section from '@components/Section';
import Container from '@components/Container';
import Map from '@components/Map';
import Button from '@components/Button';

import styles from '@styles/Home.module.scss';

import fs from "fs";
import path from "path";

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

const routeCoords = [[51.5074187, -0.1279448], [51.5074339, -0.1280059], [51.5074535, -0.1282246], [51.5075102, -0.1282287], [51.5075248, -0.1285442], [51.5076106, -0.1287367], [51.5075904, -0.1287886], [51.5077343, -0.1288858], [51.5082298, -0.1291071], [51.5082438, -0.1292508], [51.5083464, -0.1292841], [51.5082378, -0.1297819], [51.5088292, -0.1301969], [51.5089606, -0.1303222], [51.5090631, -0.1304067], [51.5093436, -0.1306409], [51.5093328, -0.1306755], [51.5093503, -0.1307044], [51.5093727, -0.1307283], [51.509373, -0.1307452], [51.5094447, -0.1308007], [51.5094699, -0.1308195], [51.5097398, -0.1310296], [51.5097514, -0.1310287], [51.5098171, -0.1311176], [51.5100523, -0.1313093], [51.5103344, -0.1315485], [51.5103632, -0.1315768], [51.5104485, -0.131624], [51.5104078, -0.1321673], [51.5110733, -0.1326652], [51.5114607, -0.132963], [51.5115097, -0.132879], [51.5116293, -0.1330102], [51.5116297, -0.1330186], [51.5120289, -0.1333734], [51.512051, -0.1333966], [51.5120942, -0.1334433], [51.5122455, -0.1336185], [51.5123734, -0.1337478], [51.5123377, -0.1338247], [51.5123874, -0.1338942], [51.5124042, -0.1338566], [51.5127549, -0.1341892], [51.5128018, -0.134183], [51.5130839, -0.1344308], [51.5135551, -0.1348905], [51.5137536, -0.135071], [51.5138581, -0.1351405], [51.513842, -0.1351995], [51.5141492, -0.1354496], [51.5141814, -0.1354773], [51.5146369, -0.13585], [51.5146848, -0.1358892], [51.5150377, -0.136178], [51.5147816, -0.1370884], [51.5147523, -0.1372018], [51.5141833, -0.1393984], [51.5140467, -0.13989], [51.5141567, -0.1399715], [51.5140787, -0.1402341], [51.5147574, -0.1407963]]

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

export default function Home({ data }) {
  return (
    <Layout>
      <Head>
        <title>Next.js Leaflet Starter</title>
        <meta name="description" content="Create mapping apps with Next.js Leaflet Starter" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <Section>
        <Container>
          <Map className={styles.homeMap} width="1280" height="800" center={DEFAULT_CENTER} zoom={12}>
            {({ TileLayer, Marker, Popup, Polyline, Circle }) => (
              <>
                <TileLayer
                  url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
                  attribution="&copy; <a href=&quot;http://osm.org/copyright&quot;>OpenStreetMap</a> contributors"
                />
                <Polyline positions={routeCoords} color="black" />
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
