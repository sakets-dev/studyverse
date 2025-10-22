import os
from typing import List, Optional, Literal
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = None
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    client = OpenAI(api_key=api_key)

# ---------------------------
# Scene schema we return
# ---------------------------

class LightConfig(BaseModel):
    type: Literal["ambient", "directional", "point"] = "ambient"
    intensity: float = 0.8
    position: Optional[List[float]] = None
    color: str = "#ffffff"

class ObjectConfig(BaseModel):
    kind: Literal["cube", "sphere", "torus", "cone", "cylinder", "tree", "lego"]
    position: List[float] = [0, 0, 0]
    rotation: List[float] = [0, 0, 0]
    scale: List[float] = [1, 1, 1]
    color: str = "#4F46E5"
    metalness: float = 0.2
    roughness: float = 0.6
    emissive: Optional[str] = None

class SceneConfig(BaseModel):
    title: str = "Custom Verse"
    background: str = "#0b1f2a"           # hex or keyword
    gradient: Optional[List[str]] = None  # for skybox fade
    lights: List[LightConfig] = [LightConfig()]
    objects: List[ObjectConfig] = []
    environment: Optional[Literal["sunset","dawn","night","studio","city","forest","apartment","warehouse","park","lobby","none"]] = "night"
    camera: List[float] = [6, 4, 8]

class GenerateReq(BaseModel):
    prompt: str

# ---------------------------
# Fallback rules (no API key)
# ---------------------------

def rule_based_scene(prompt: str) -> SceneConfig:
    p = prompt.lower()
    if "lego" in p:
        return SceneConfig(
            title="Lego City",
            background="#0c2330",
            gradient=["#0c2330","#0b3b3b","#127369"],
            environment="studio",
            lights=[LightConfig(type="ambient", intensity=0.8),
                    LightConfig(type="directional", intensity=1.0, position=[5,6,5])],
            objects=[
                ObjectConfig(kind="lego", color="#F7B500", scale=[1.6,0.6,1.0], position=[0,0.3,0]),
                ObjectConfig(kind="lego", color="#E63946", scale=[1.0,0.6,1.0], position=[-2,0.3,-1]),
                ObjectConfig(kind="lego", color="#2A9D8F", scale=[1.2,0.6,0.8], position=[2,0.3,1]),
            ],
            camera=[7, 4, 9]
        )
    if "ocean" in p or "sea" in p:
        return SceneConfig(
            title="Calm Ocean",
            background="#04202b",
            gradient=["#03131a","#073d4b","#0d8a8a"],
            environment="dawn",
            lights=[LightConfig(type="ambient", intensity=0.7, color="#bde0fe"),
                    LightConfig(type="directional", intensity=0.8, position=[-4,6,4], color="#b9fbc0")],
            objects=[
                ObjectConfig(kind="sphere", color="#5bc0eb", scale=[2.4,0.1,2.4], position=[0,-0.5,0], metalness=0.1, roughness=0.8),
                ObjectConfig(kind="torus", color="#90e0ef", scale=[0.8,0.8,0.8], position=[-1,0.2,0], rotation=[1.2,0,0]),
                ObjectConfig(kind="torus", color="#caf0f8", scale=[0.6,0.6,0.6], position=[1,0.2,1], rotation=[1.2,0,0]),
            ],
            camera=[6, 4, 8]
        )
    if "forest" in p or "tree" in p or "nature" in p:
        return SceneConfig(
            title="Cyber Forest",
            background="#081a14",
            gradient=["#081a14","#0a3d2e","#0fbf8f"],
            environment="forest",
            lights=[LightConfig(type="ambient", intensity=0.8, color="#d4f8e8"),
                    LightConfig(type="point", intensity=0.9, position=[0,3,0], color="#00ffd0")],
            objects=[
                ObjectConfig(kind="cone", color="#1dd3b0", scale=[1.4,2.2,1.4], position=[-1,0.2,-0.5]),
                ObjectConfig(kind="cone", color="#12b886", scale=[1.2,1.8,1.2], position=[1.2,0.2,0.8]),
                ObjectConfig(kind="cylinder", color="#8d5524", scale=[0.3,1.0,0.3], position=[-1,0.5,-0.5]),
                ObjectConfig(kind="cylinder", color="#8d5524", scale=[0.3,0.8,0.3], position=[1.2,0.4,0.8]),
            ],
            camera=[6, 4, 8]
        )
    # default playful space
    return SceneConfig(
        title="Neon Playground",
        background="#0c1620",
        gradient=["#0c1620", "#11293f", "#0fa3b1"],
        environment="night",
        lights=[LightConfig(type="ambient", intensity=0.8),
                LightConfig(type="point", intensity=1.0, position=[3,4,3], color="#8ecae6")],
        objects=[
            ObjectConfig(kind="cube", color="#ffb703", scale=[1.2,1.2,1.2], position=[-1,0.8,0]),
            ObjectConfig(kind="sphere", color="#fb8500", scale=[0.9,0.9,0.9], position=[1,0.9,0]),
            ObjectConfig(kind="torus", color="#9b5de5", scale=[0.8,0.8,0.8], position=[0,0.3,1.3]),
        ],
        camera=[7, 4, 9]
    )

def llm_scene(prompt: str) -> SceneConfig:
    """Ask GPT to emit a SceneConfig-like JSON. We guard + coerce."""
    sys = (
        "You generate compact JSON scene configs for a WebGL 3D world. "
        "Only return JSON with keys: title, background, gradient (array of 2-4 hex colors), "
        "environment (one of sunset,dawn,night,studio,city,forest,apartment,warehouse,park,lobby,none), "
        "camera [x,y,z], lights (list of {type,intensity,position?,color}), "
        "objects (list of {kind in [cube,sphere,torus,cone,cylinder,lego,tree], "
        "position [x,y,z], rotation [x,y,z], scale [x,y,z], color hex, metalness, roughness, emissive?}). "
        "Values must be reasonable floats. Output JSON only."
    )
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": sys},
                {"role": "user", "content": f"Make a scene for: {prompt}"},
            ],
            temperature=0.7,
            max_tokens=600,
        )
        import json
        data = json.loads(resp.choices[0].message.content)
        return SceneConfig(**data)
    except Exception:
        # fall back if parsing/limits fail
        return rule_based_scene(prompt)

@app.post("/generate", response_model=SceneConfig)
def generate(req: GenerateReq):
    if client is None:
        return rule_based_scene(req.prompt)
    return llm_scene(req.prompt)

@app.get("/health")
def health():
    return {"ok": True}
