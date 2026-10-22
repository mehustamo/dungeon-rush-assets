# dungeon-rush-assets

**Dungeon Rushin 3D-assetit.** Ei pelirepossa: tänne julkaistaan versioidut paketit GitHub Releaseina,
ja peli hakee ne buildissa manifestin (`assets.manifest.json`) osoittamasta URL:sta ja tarkistaa **sha256:n**.

## Konventiot

| Asia | Sääntö |
|---|---|
| Release-tagi | `<paketti>@<versio>`, esim. `kenney-mini-dungeon@2.0` |
| Tiedostot | `<paketti>-<versio>.zip` + `<paketti>-<versio>.zip.sha256` |
| Zipin juuri | `<paketti>/…` — suhteelliset polut säilyvät (glb:n tekstuuriviittaukset ovat suhteellisia) |
| Metatiedot | `PACK.json` zipin sisällä: nimi, versio, lisenssi, upstream |
| Kuluttaja | pelirepon `assets.manifest.json` → `tools/fetch_assets.py` |

Repo on **julkinen**, koska CI lataa releaseista ilman tunnuksia. Älä lisää tänne mitään, mitä ei saa jakaa.
Vain CC0/lisensoitu sisältö, lisenssi aina mukaan pakettiin.

## Paketin teko

```bash
# 1. Kokoa lähdekansio (esim. Kenneyn zipistä puretut GLB:t + tekstuurit)
# 2. Rakenna zip + sha256 ja tulosta manifestirivi
tools/pack.py build --name kenney-mini-dungeon --version 2.0 --src /polku/paketti/ \
    --license CC0-1.0 --upstream https://kenney.nl/assets/mini-dungeon

# 3. Julkaise
tools/pack.py publish --name kenney-mini-dungeon --version 2.0 \
    --notes "Kenney Mini Dungeon GLB, 30 mallia"
```

`build` tulostaa valmiin JSON-lohkon, jonka voi liittää pelirepon `assets.manifest.json`iin.

## Paketit

- `kenney-mini-dungeon@2.0` — Kenney Mini Dungeon (CC0), 30 GLB-mallia + `colormap.png`.
