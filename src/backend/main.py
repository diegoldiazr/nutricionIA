from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .config.settings import settings
from .services import DatabaseService, NotebookLMConnector, OpenRouterService
from .agents import (
    KnowledgeAgent,
    NutritionAgent,
    UserAgent,
    MealPlannerAgent,
    ProgressAgent,
    RecommendationAgent,
    MemoryAgent,
    OrchestrationAgent
)
from .routers import users_router, meals_router, nutrition_router, progress_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Initializing Nutrition Assistant API...")
    
    # Initialize database
    db_service = DatabaseService()
    await db_service.init_db()
    
    # Initialize services
    notebooklm = NotebookLMConnector(
        token=settings.NOTION_TOKEN,
        workspace_url=settings.NOTION_WORKSPACE
    )
    openrouter = OpenRouterService(api_key=settings.OPENROUTER_API_KEY)
    
    # Initialize agents
    knowledge_agent = KnowledgeAgent(connector=notebooklm)
    user_agent = UserAgent(database=db_service)
    nutrition_agent = NutritionAgent(
        knowledge_agent=knowledge_agent,
        database=db_service
    )
    
    # Meal Planner needs knowledge + user
    meal_planner_agent = MealPlannerAgent(
        knowledge_agent=knowledge_agent,
        database=db_service,
        user_agent=user_agent
    )
    
    # Progress agent
    progress_agent = ProgressAgent(
        user_agent=user_agent,
        nutrition_agent=nutrition_agent
    )
    
    # Memory agent
    memory_agent = MemoryAgent(database=db_service)
    
    # Recommendation agent
    recommendation_agent = RecommendationAgent(
        nutrition_agent=nutrition_agent,
        progress_agent=progress_agent,
        user_agent=user_agent
    )
    
    # Orchestrator - central controller
    orchestrator = OrchestrationAgent({
        'knowledge': knowledge_agent,
        'nutrition': nutrition_agent,
        'user': user_agent,
        'meal_planner': meal_planner_agent,
        'progress': progress_agent,
        'recommendation': recommendation_agent,
        'memory': memory_agent,
    })
    
    # Store in app state
    app.state.db_service = db_service
    app.state.knowledge_agent = knowledge_agent
    app.state.nutrition_agent = nutrition_agent
    app.state.user_agent = user_agent
    app.state.meal_planner_agent = meal_planner_agent
    app.state.progress_agent = progress_agent
    app.state.recommendation_agent = recommendation_agent
    app.state.memory_agent = memory_agent
    app.state.orchestrator = orchestrator
    
    print("All agents loaded and ready.")
    print("API startup complete.")
    yield
    
    # Shutdown
    print("Shutting down API...")

app = FastAPI(
    title="Nutrition AI Assistant",
    description="Multi-agent AI nutrition assistant",
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users_router)
app.include_router(meals_router)
app.include_router(nutrition_router)
app.include_router(progress_router)

@app.get("/")
async def root():
    return {"message": "Nutrition Assistant API", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/health/agents")
async def agents_health(app_state=app.state):
    """Check health of all agents."""
    health = {}
    for name, agent in {
        'knowledge': app_state.knowledge_agent,
        'nutrition': app_state.nutrition_agent,
        'user': app_state.user_agent,
        'meal_planner': app_state.meal_planner_agent,
        'progress': app_state.progress_agent,
        'recommendation': app_state.recommendation_agent,
        'memory': app_state.memory_agent,
        'orchestrator': app_state.orchestrator,
    }.items():
        try:
            if hasattr(agent, 'health'):
                health[name] = await agent.health()
            else:
                health[name] = 'operational'
        except Exception as e:
            health[name] = f'error: {str(e)}'
    return health

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
