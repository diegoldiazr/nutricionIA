"""
Fallback Meal Database - Smart meal suggestions when NotebookLM is unavailable.

This database provides varied, realistic meals across:
- All meal types (breakfast, lunch, dinner, snack)
- Different calorie ranges
- Multiple dietary restrictions
- Various cooking equipment

All nutrition data is approximate and based on standard portion sizes.
"""

from typing import Dict, Any, List, Tuple

# =============================================================================
# Meal Database
# =============================================================================

FALLBACK_MEALS: List[Dict[str, Any]] = [
    # =========================================================================
    # BREAKFAST OPTIONS
    # =========================================================================
    {
        "name": "Greek Yogurt Parfait",
        "meal_type": "breakfast",
        "ingredients": [
            "200g Greek yogurt (2% fat)",
            "50g granola",
            "100g mixed berries",
            "1 tbsp honey",
            "10g chia seeds",
        ],
        "instructions": [
            "Layer yogurt in a glass or bowl",
            "Add granola on top",
            "Add fresh berries",
            "Drizzle with honey",
            "Sprinkle chia seeds",
        ],
        "nutrition": {
            "calories": 350,
            "protein": 18,
            "carbs": 45,
            "fat": 12,
        },
        "tags": ["vegetarian", "high_protein", "quick", "no_cooking"],
        "equipment": ["stove"],
        "prep_time_minutes": 5,
        "cook_time_minutes": 0,
    },
    {
        "name": "Egg White Vegetable Omelette",
        "meal_type": "breakfast",
        "ingredients": [
            "4 egg whites",
            "50g spinach",
            "30g bell pepper",
            "30g mushrooms",
            "20g onion",
            "Salt and pepper to taste",
        ],
        "instructions": [
            "Whisk egg whites with salt and pepper",
            "Sauté vegetables in a non-stick pan for 2 minutes",
            "Pour egg whites over vegetables",
            "Cook on medium until set, about 3 minutes",
            "Fold omelette in half and serve",
        ],
        "nutrition": {
            "calories": 140,
            "protein": 18,
            "carbs": 8,
            "fat": 4,
        },
        "tags": ["high_protein", "low_carb", "gluten_free", "quick"],
        "equipment": ["stove", "oven"],
        "prep_time_minutes": 5,
        "cook_time_minutes": 8,
    },
    {
        "name": "Overnight Oats with Banana",
        "meal_type": "breakfast",
        "ingredients": [
            "80g rolled oats",
            "200ml almond milk",
            "1 medium banana",
            "20g walnuts",
            "1 tsp cinnamon",
            "150g Greek yogurt",
        ],
        "instructions": [
            "Mix oats with almond milk in a jar",
            "Add cinnamon and stir",
            "Slice banana and add on top",
            "Add walnuts",
            "Refrigerate overnight (or at least 4 hours)",
            "Top with Greek yogurt before serving",
        ],
        "nutrition": {
            "calories": 420,
            "protein": 16,
            "carbs": 58,
            "fat": 16,
        },
        "tags": ["vegetarian", "meal_prep", "no_cooking"],
        "equipment": ["stove"],
        "prep_time_minutes": 5,
        "cook_time_minutes": 0,
    },
    {
        "name": "Protein Pancakes",
        "meal_type": "breakfast",
        "ingredients": [
            "60g oat flour",
            "1 scoop protein powder (vanilla)",
            "100ml milk",
            "1 whole egg",
            "50g blueberries",
            "10g butter",
            "30g maple syrup",
        ],
        "instructions": [
            "Mix oat flour, protein powder, milk, and egg",
            "Heat non-stick pan with butter",
            "Pour small amounts of batter to form pancakes",
            "Cook until bubbles form, flip and cook other side",
            "Serve with blueberries and maple syrup",
        ],
        "nutrition": {
            "calories": 450,
            "protein": 32,
            "carbs": 52,
            "fat": 14,
        },
        "tags": ["high_protein", "sweet", "quick"],
        "equipment": ["stove"],
        "prep_time_minutes": 5,
        "cook_time_minutes": 15,
    },
    {
        "name": "Avocado Toast with Poached Eggs",
        "meal_type": "breakfast",
        "ingredients": [
            "2 slices whole grain bread",
            "1 medium avocado",
            "2 eggs",
            "Salt, pepper, and chili flakes",
            "1 tsp lemon juice",
            "10g microgreens",
        ],
        "instructions": [
            "Toast bread until golden",
            "Mash avocado with lemon juice, salt, and pepper",
            "Poach eggs in simmering water for 3 minutes",
            "Spread avocado on toast",
            "Top with poached eggs",
            "Sprinkle with chili flakes and microgreens",
        ],
        "nutrition": {
            "calories": 420,
            "protein": 18,
            "carbs": 32,
            "fat": 26,
        },
        "tags": ["vegetarian", "balanced", "quick"],
        "equipment": ["stove", "oven"],
        "prep_time_minutes": 5,
        "cook_time_minutes": 10,
    },

    # =========================================================================
    # LUNCH OPTIONS
    # =========================================================================
    {
        "name": "Grilled Chicken Quinoa Bowl",
        "meal_type": "lunch",
        "ingredients": [
            "150g chicken breast",
            "80g quinoa",
            "100g roasted vegetables (zucchini, eggplant)",
            "50g chickpeas",
            "30g feta cheese",
            "20g tzatziki sauce",
        ],
        "instructions": [
            "Cook quinoa according to package directions",
            "Season chicken with herbs and grill for 6-7 minutes per side",
            "Roast vegetables at 200°C for 20 minutes",
            "Slice grilled chicken",
            "Assemble bowl with quinoa base, chicken, vegetables, and chickpeas",
            "Top with feta and drizzle with tzatziki",
        ],
        "nutrition": {
            "calories": 580,
            "protein": 48,
            "carbs": 52,
            "fat": 22,
        },
        "tags": ["high_protein", "balanced", "meal_prep"],
        "equipment": ["stove", "oven", "airfryer"],
        "prep_time_minutes": 15,
        "cook_time_minutes": 30,
    },
    {
        "name": "Tuna Salad Lettuce Wraps",
        "meal_type": "lunch",
        "ingredients": [
            "120g canned tuna (in water)",
            "30g Greek yogurt",
            "20g celery",
            "15g red onion",
            "1 tbsp lemon juice",
            "4 large lettuce leaves",
            "Salt and pepper",
        ],
        "instructions": [
            "Drain tuna and place in mixing bowl",
            "Finely chop celery and red onion",
            "Mix tuna with yogurt, vegetables, and lemon juice",
            "Season with salt and pepper",
            "Spoon mixture into lettuce leaves",
            "Serve immediately or chill for later",
        ],
        "nutrition": {
            "calories": 220,
            "protein": 35,
            "carbs": 8,
            "fat": 6,
        },
        "tags": ["high_protein", "low_carb", "low_calorie", "quick", "no_cooking"],
        "equipment": [],
        "prep_time_minutes": 10,
        "cook_time_minutes": 0,
    },
    {
        "name": "Turkey and Hummus Wrap",
        "meal_type": "lunch",
        "ingredients": [
            "100g sliced turkey breast",
            "50g hummus",
            "1 whole wheat tortilla",
            "30g arugula",
            "50g roasted red peppers",
            "10g sun-dried tomatoes",
        ],
        "instructions": [
            "Spread hummus evenly on tortilla",
            "Layer turkey slices on hummus",
            "Add arugula, roasted peppers, and sun-dried tomatoes",
            "Roll tightly, tucking in sides",
            "Cut diagonally and serve",
        ],
        "nutrition": {
            "calories": 380,
            "protein": 32,
            "carbs": 30,
            "fat": 14,
        },
        "tags": ["high_protein", "quick", "balanced"],
        "equipment": [],
        "prep_time_minutes": 5,
        "cook_time_minutes": 0,
    },
    {
        "name": "Mediterranean Chickpea Salad",
        "meal_type": "lunch",
        "ingredients": [
            "150g cooked chickpeas",
            "100g cucumber",
            "100g cherry tomatoes",
            "50g kalamata olives",
            "40g feta cheese",
            "20g red onion",
            "30ml olive oil",
            "15ml red wine vinegar",
            "Oregano and salt",
        ],
        "instructions": [
            "Drain and rinse chickpeas",
            "Chop cucumber, tomatoes, and red onion",
            "Combine all vegetables in a bowl",
            "Add olives and crumbled feta",
            "Whisk olive oil with vinegar and oregano",
            "Drizzle dressing over salad and toss",
        ],
        "nutrition": {
            "calories": 480,
            "protein": 18,
            "carbs": 42,
            "fat": 28,
        },
        "tags": ["vegetarian", "balanced", "meal_prep", "no_cooking"],
        "equipment": [],
        "prep_time_minutes": 15,
        "cook_time_minutes": 0,
    },
    {
        "name": "Salmon Poke Bowl",
        "meal_type": "lunch",
        "ingredients": [
            "120g sushi-grade salmon",
            "80g sushi rice",
            "50g edamame",
            "50g cucumber",
            "30g avocado",
            "20g seaweed salad",
            "15ml soy sauce",
            "5ml sesame oil",
            "Sesame seeds",
        ],
        "instructions": [
            "Cook sushi rice and let cool slightly",
            "Cube salmon into bite-sized pieces",
            "Slice cucumber and avocado",
            "Divide rice into bowls",
            "Arrange salmon, edamame, cucumber, avocado on rice",
            "Top with seaweed salad",
            "Mix soy sauce and sesame oil for dressing",
            "Drizzle and sprinkle with sesame seeds",
        ],
        "nutrition": {
            "calories": 520,
            "protein": 38,
            "carbs": 48,
            "fat": 22,
        },
        "tags": ["high_protein", "balanced", "quick"],
        "equipment": ["stove"],
        "prep_time_minutes": 15,
        "cook_time_minutes": 15,
    },

    # =========================================================================
    # DINNER OPTIONS
    # =========================================================================
    {
        "name": "Grilled Chicken with Sweet Potato",
        "meal_type": "dinner",
        "ingredients": [
            "180g chicken breast",
            "200g sweet potato",
            "150g broccoli",
            "10g olive oil",
            "Rosemary, thyme, garlic powder",
            "Salt and pepper",
        ],
        "instructions": [
            "Preheat oven to 200°C",
            "Cut sweet potato into wedges, toss with olive oil and seasonings",
            "Roast sweet potato for 25 minutes",
            "Season chicken with herbs",
            "Grill chicken 6-7 minutes per side until internal temp reaches 74°C",
            "Steam broccoli for 5 minutes",
            "Serve chicken with sweet potato wedges and broccoli",
        ],
        "nutrition": {
            "calories": 480,
            "protein": 45,
            "carbs": 48,
            "fat": 12,
        },
        "tags": ["high_protein", "balanced", "meal_prep", "gluten_free"],
        "equipment": ["stove", "oven", "airfryer"],
        "prep_time_minutes": 10,
        "cook_time_minutes": 30,
    },
    {
        "name": "Lean Beef Stir Fry",
        "meal_type": "dinner",
        "ingredients": [
            "150g lean beef strips",
            "150g broccoli florets",
            "80g bell peppers",
            "50g snap peas",
            "30g soy sauce",
            "10ml sesame oil",
            "2g ginger",
            "2g garlic",
            "100g jasmine rice",
        ],
        "instructions": [
            "Cook jasmine rice according to package directions",
            "Heat wok or large pan over high heat",
            "Stir fry beef strips for 2-3 minutes, remove and set aside",
            "Add vegetables and stir fry for 3-4 minutes",
            "Add ginger and garlic, cook 30 seconds",
            "Return beef to pan, add soy sauce and sesame oil",
            "Toss everything together and serve over rice",
        ],
        "nutrition": {
            "calories": 580,
            "protein": 42,
            "carbs": 55,
            "fat": 20,
        },
        "tags": ["high_protein", "quick", "balanced"],
        "equipment": ["stove"],
        "prep_time_minutes": 10,
        "cook_time_minutes": 20,
    },
    {
        "name": "Baked Cod with Vegetables",
        "meal_type": "dinner",
        "ingredients": [
            "180g cod fillet",
            "150g zucchini",
            "100g cherry tomatoes",
            "50g onion",
            "30ml olive oil",
            "Lemon juice",
            "Oregano, basil, salt, pepper",
        ],
        "instructions": [
            "Preheat oven to 200°C",
            "Place cod in center of baking dish",
            "Slice zucchini and tomatoes, arrange around fish",
            "Add onion slices on top",
            "Drizzle with olive oil and lemon juice",
            "Season with herbs, salt, and pepper",
            "Bake for 20 minutes until fish flakes easily",
        ],
        "nutrition": {
            "calories": 340,
            "protein": 38,
            "carbs": 14,
            "fat": 16,
        },
        "tags": ["high_protein", "low_carb", "gluten_free", "meal_prep"],
        "equipment": ["oven"],
        "prep_time_minutes": 10,
        "cook_time_minutes": 20,
    },
    {
        "name": "Turkey Meatballs with Zucchini Noodles",
        "meal_type": "dinner",
        "ingredients": [
            "150g ground turkey",
            "30g breadcrumbs",
            "1 egg white",
            "Italian seasoning, garlic powder, salt",
            "200g zucchini (spiralized)",
            "100g marinara sauce (low sugar)",
            "20g parmesan cheese",
        ],
        "instructions": [
            "Mix turkey, breadcrumbs, egg white, and seasonings",
            "Form into 6 meatballs",
            "Bake meatballs at 200°C for 18-20 minutes",
            "Spiralize zucchini into noodles",
            "Heat marinara sauce in pan",
            "Add zucchini noodles and cook 2-3 minutes",
            "Top with meatballs and parmesan",
        ],
        "nutrition": {
            "calories": 420,
            "protein": 40,
            "carbs": 22,
            "fat": 20,
        },
        "tags": ["high_protein", "low_carb", "meal_prep"],
        "equipment": ["stove", "oven"],
        "prep_time_minutes": 15,
        "cook_time_minutes": 25,
    },
    {
        "name": "Shrimp and Vegetable Skewers",
        "meal_type": "dinner",
        "ingredients": [
            "180g large shrimp",
            "100g bell pepper",
            "80g zucchini",
            "80g onion",
            "30ml olive oil",
            "Garlic, paprika, salt, pepper",
            "100g couscous",
            "15g fresh parsley",
        ],
        "instructions": [
            "Soak wooden skewers in water",
            "Cut vegetables into chunks",
            "Marinate shrimp with oil and spices",
            "Alternate shrimp and vegetables on skewers",
            "Grill or broil skewers for 2-3 minutes per side",
            "Cook couscous according to package",
            "Serve skewers over couscous with parsley",
        ],
        "nutrition": {
            "calories": 460,
            "protein": 38,
            "carbs": 40,
            "fat": 18,
        },
        "tags": ["high_protein", "quick", "balanced"],
        "equipment": ["stove", "oven", "airfryer", "bbq"],
        "prep_time_minutes": 15,
        "cook_time_minutes": 15,
    },
    {
        "name": "Lentil Soup with Whole Grain Bread",
        "meal_type": "dinner",
        "ingredients": [
            "100g dried lentils",
            "100g carrots",
            "80g celery",
            "50g onion",
            "10g garlic",
            "500ml vegetable broth",
            "Cumin, turmeric, salt, pepper",
            "2 slices whole grain bread",
            "10g butter",
        ],
        "instructions": [
            "Rinse lentils and set aside",
            "Dice carrots, celery, and onion",
            "Sauté vegetables with garlic in pot",
            "Add spices and cook 1 minute",
            "Add lentils and broth, bring to boil",
            "Simmer 25-30 minutes until lentils tender",
            "Season to taste",
            "Serve with whole grain bread and butter",
        ],
        "nutrition": {
            "calories": 450,
            "protein": 24,
            "carbs": 68,
            "fat": 10,
        },
        "tags": ["vegetarian", "high_fiber", "meal_prep", "comfort_food"],
        "equipment": ["stove"],
        "prep_time_minutes": 15,
        "cook_time_minutes": 40,
    },

    # =========================================================================
    # SNACK OPTIONS
    # =========================================================================
    {
        "name": "Protein Energy Balls",
        "meal_type": "snack",
        "ingredients": [
            "50g rolled oats",
            "30g protein powder",
            "20g peanut butter",
            "15g honey",
            "10g dark chocolate chips",
            "10g chia seeds",
        ],
        "instructions": [
            "Mix all ingredients in a bowl",
            "Refrigerate mixture for 30 minutes",
            "Roll into 6 equal balls",
            "Store in refrigerator up to 1 week",
        ],
        "nutrition": {
            "calories": 180,
            "protein": 12,
            "carbs": 18,
            "fat": 8,
        },
        "tags": ["vegetarian", "high_protein", "meal_prep", "no_cooking", "sweet"],
        "equipment": [],
        "prep_time_minutes": 10,
        "cook_time_minutes": 0,
    },
    {
        "name": "Apple with Almond Butter",
        "meal_type": "snack",
        "ingredients": [
            "1 medium apple",
            "20g almond butter",
            "5g granola (optional)",
        ],
        "instructions": [
            "Slice apple into wedges",
            "Spread almond butter on side",
            "Sprinkle with granola if desired",
        ],
        "nutrition": {
            "calories": 200,
            "protein": 5,
            "carbs": 25,
            "fat": 11,
        },
        "tags": ["vegetarian", "vegan", "quick", "no_cooking", "sweet"],
        "equipment": [],
        "prep_time_minutes": 2,
        "cook_time_minutes": 0,
    },
    {
        "name": "Cottage Cheese with Pineapple",
        "meal_type": "snack",
        "ingredients": [
            "150g cottage cheese (low fat)",
            "80g fresh pineapple chunks",
            "5g honey",
            "5g mint leaves (optional)",
        ],
        "instructions": [
            "Place cottage cheese in bowl",
            "Top with fresh pineapple chunks",
            "Drizzle with honey",
            "Garnish with mint if desired",
        ],
        "nutrition": {
            "calories": 160,
            "protein": 18,
            "carbs": 16,
            "fat": 4,
        },
        "tags": ["vegetarian", "high_protein", "quick", "no_cooking", "sweet"],
        "equipment": [],
        "prep_time_minutes": 3,
        "cook_time_minutes": 0,
    },
    {
        "name": "Hummus and Veggie Sticks",
        "meal_type": "snack",
        "ingredients": [
            "60g hummus",
            "80g carrot sticks",
            "80g celery sticks",
            "50g bell pepper strips",
            "30g cucumber slices",
        ],
        "instructions": [
            "Arrange vegetable sticks on plate",
            "Place hummus in center dip bowl",
            "Serve immediately or store vegetables in water for crunch",
        ],
        "nutrition": {
            "calories": 180,
            "protein": 6,
            "carbs": 20,
            "fat": 10,
        },
        "tags": ["vegetarian", "vegan", "low_calorie", "quick", "no_cooking"],
        "equipment": [],
        "prep_time_minutes": 5,
        "cook_time_minutes": 0,
    },
    {
        "name": "Rice Cakes with Smoked Salmon",
        "meal_type": "snack",
        "ingredients": [
            "2 rice cakes",
            "60g smoked salmon",
            "30g cream cheese (light)",
            "10g capers",
            "10g red onion slices",
            "Lemon juice",
            "Dill",
        ],
        "instructions": [
            "Spread cream cheese on rice cakes",
            "Top with smoked salmon pieces",
            "Add red onion and capers",
            "Squeeze lemon juice and garnish with dill",
        ],
        "nutrition": {
            "calories": 200,
            "protein": 14,
            "carbs": 16,
            "fat": 10,
        },
        "tags": ["high_protein", "quick", "no_cooking"],
        "equipment": [],
        "prep_time_minutes": 5,
        "cook_time_minutes": 0,
    },

    # =========================================================================
    # VEGETARIAN/VEGAN OPTIONS (for lunch/dinner)
    # =========================================================================
    {
        "name": "Tofu Stir Fry with Brown Rice",
        "meal_type": "dinner",
        "ingredients": [
            "150g firm tofu",
            "150g broccoli",
            "80g bell peppers",
            "50g snap peas",
            "30ml soy sauce",
            "10ml sesame oil",
            "2g ginger",
            "2g garlic",
            "80g brown rice",
        ],
        "instructions": [
            "Press tofu and cut into cubes",
            "Cook brown rice according to package",
            "Pan fry tofu until golden on all sides",
            "Stir fry vegetables with ginger and garlic",
            "Add tofu back, pour soy sauce and sesame oil",
            "Serve over brown rice",
        ],
        "nutrition": {
            "calories": 450,
            "protein": 24,
            "carbs": 52,
            "fat": 18,
        },
        "tags": ["vegetarian", "vegan", "balanced", "meal_prep"],
        "equipment": ["stove"],
        "prep_time_minutes": 15,
        "cook_time_minutes": 30,
    },
    {
        "name": "Egg and Black Bean Burrito",
        "meal_type": "breakfast",
        "ingredients": [
            "2 eggs",
            "80g black beans",
            "50g bell pepper",
            "30g onion",
            "1 whole wheat tortilla",
            "20g salsa",
            "15g avocado",
            "Salt and pepper",
        ],
        "instructions": [
            "Scramble eggs with salt and pepper",
            "Sauté diced peppers and onions",
            "Warm black beans in pan",
            "Heat tortilla",
            "Layer eggs, beans, vegetables on tortilla",
            "Top with salsa and avocado",
            "Roll and serve",
        ],
        "nutrition": {
            "calories": 420,
            "protein": 22,
            "carbs": 42,
            "fat": 18,
        },
        "tags": ["vegetarian", "high_protein", "quick", "balanced"],
        "equipment": ["stove"],
        "prep_time_minutes": 5,
        "cook_time_minutes": 10,
    },
    {
        "name": "White Bean and Spinach Soup",
        "meal_type": "dinner",
        "ingredients": [
            "150g canned cannellini beans",
            "100g fresh spinach",
            "80g carrot",
            "60g celery",
            "50g onion",
            "10g garlic",
            "500ml vegetable broth",
            "Rosemary, thyme, salt, pepper",
            "20g parmesan (optional)",
        ],
        "instructions": [
            "Dice carrot, celery, and onion",
            "Sauté vegetables with garlic",
            "Add broth and herbs, bring to boil",
            "Add beans and simmer 15 minutes",
            "Stir in spinach until wilted",
            "Season and top with parmesan",
        ],
        "nutrition": {
            "calories": 280,
            "protein": 16,
            "carbs": 38,
            "fat": 6,
        },
        "tags": ["vegetarian", "vegan", "high_fiber", "meal_prep", "comfort_food"],
        "equipment": ["stove"],
        "prep_time_minutes": 10,
        "cook_time_minutes": 25,
    },

    # =========================================================================
    # AIRFRYER-SPECIFIC RECIPES
    # =========================================================================
    {
        "name": "Air Fryer Chicken Wings",
        "meal_type": "dinner",
        "ingredients": [
            "200g chicken wings",
            "10g buffalo sauce",
            "5g garlic powder",
            "Salt and pepper",
            "20g blue cheese dressing (for dipping)",
        ],
        "instructions": [
            "Pat wings dry with paper towel",
            "Season with salt, pepper, and garlic powder",
            "Preheat air fryer to 200°C",
            "Cook wings for 12-15 minutes, flipping halfway",
            "Toss with buffalo sauce",
            "Serve with blue cheese dressing",
        ],
        "nutrition": {
            "calories": 380,
            "protein": 32,
            "carbs": 4,
            "fat": 26,
        },
        "tags": ["high_protein", "low_carb", "quick", "keto"],
        "equipment": ["airfryer"],
        "prep_time_minutes": 5,
        "cook_time_minutes": 15,
    },
    {
        "name": "Air Fryer Salmon Fillet",
        "meal_type": "dinner",
        "ingredients": [
            "180g salmon fillet",
            "10ml olive oil",
            "Lemon pepper seasoning",
            "10g dill (fresh)",
            "100g asparagus",
        ],
        "instructions": [
            "Brush salmon with olive oil",
            "Season with lemon pepper",
            "Preheat air fryer to 190°C",
            "Air fry salmon for 8-10 minutes",
            "In last 3 minutes, add asparagus to air fryer",
            "Garnish with fresh dill",
        ],
        "nutrition": {
            "calories": 400,
            "protein": 40,
            "carbs": 4,
            "fat": 24,
        },
        "tags": ["high_protein", "low_carb", "gluten_free", "quick", "keto"],
        "equipment": ["airfryer"],
        "prep_time_minutes": 5,
        "cook_time_minutes": 10,
    },
    {
        "name": "Air Fryer Falafel",
        "meal_type": "lunch",
        "ingredients": [
            "100g canned chickpeas",
            "30g onion",
            "10g parsley",
            "10g cilantro",
            "5g garlic",
            "5g cumin",
            "Salt and pepper",
            "20g tahini sauce",
        ],
        "instructions": [
            "Drain chickpeas, pat very dry",
            "Blend all ingredients in food processor",
            "Form into 6 small patties",
            "Preheat air fryer to 180°C",
            "Air fry for 10-12 minutes, flipping halfway",
            "Serve with tahini sauce",
        ],
        "nutrition": {
            "calories": 320,
            "protein": 14,
            "carbs": 38,
            "fat": 14,
        },
        "tags": ["vegetarian", "vegan", "balanced"],
        "equipment": ["airfryer"],
        "prep_time_minutes": 15,
        "cook_time_minutes": 12,
    },

    # =========================================================================
    # THERMOMIX / HIGH-END EQUIPMENT
    # =========================================================================
    {
        "name": "Thermomix Vegetable Soup",
        "meal_type": "dinner",
        "ingredients": [
            "100g carrot",
            "80g potato",
            "80g zucchini",
            "60g celery",
            "50g leek",
            "500ml vegetable broth",
            "Bay leaf, thyme, salt, pepper",
        ],
        "instructions": [
            "Cut vegetables into pieces",
            "Add all to Thermomix bowl",
            "Add broth and seasonings",
            "Cook on Varoma temp, speed 1, for 25 minutes",
            "Blend on speed 5-10 for silky smooth texture",
            "Serve hot",
        ],
        "nutrition": {
            "calories": 180,
            "protein": 5,
            "carbs": 35,
            "fat": 2,
        },
        "tags": ["vegetarian", "vegan", "low_calorie", "meal_prep", "comfort_food"],
        "equipment": ["thermomix", "stove"],
        "prep_time_minutes": 15,
        "cook_time_minutes": 30,
    },
    {
        "name": "Thermomix Protein Hummus",
        "meal_type": "snack",
        "ingredients": [
            "200g canned chickpeas",
            "40g tahini",
            "30ml lemon juice",
            "10g garlic",
            "20ml olive oil",
            "Cumin, salt to taste",
        ],
        "instructions": [
            "Add all ingredients except oil to Thermomix",
            "Blend on speed 5 for 2 minutes",
            "With motor running, drizzle in olive oil",
            "Blend until smooth and creamy",
            "Serve with veggies or pita",
        ],
        "nutrition": {
            "calories": 220,
            "protein": 8,
            "carbs": 18,
            "fat": 14,
        },
        "tags": ["vegetarian", "vegan", "high_fiber", "quick"],
        "equipment": ["thermomix"],
        "prep_time_minutes": 5,
        "cook_time_minutes": 3,
    },
]


# =============================================================================
# Helper Functions
# =============================================================================

def get_meals_for_calorie_range(
    meals: List[Dict[str, Any]],
    target_calories: int,
    calorie_range: Tuple[int, int] = None
) -> List[Dict[str, Any]]:
    """
    Filter meals suitable for a calorie target and range.

    Args:
        meals: Full meal database
        target_calories: Target calories for the meal
        calorie_range: Optional (min, max) tuple to filter by meal type norms

    Returns:
        Filtered list of meals appropriate for the calorie target
    """
    if calorie_range:
        min_cal, max_cal = calorie_range
    else:
        # Allow 50% flexibility around target
        min_cal = target_calories * 0.5
        max_cal = target_calories * 1.5

    candidates = [
        m for m in meals
        if min_cal <= m["nutrition"]["calories"] <= max_cal
    ]

    # If too few candidates, relax constraints
    if len(candidates) < 3:
        candidates = [
            m for m in meals
            if m["nutrition"]["calories"] <= max_cal * 1.5
        ]

    return candidates


def get_meals_by_type(
    meals: List[Dict[str, Any]],
    meal_type: str
) -> List[Dict[str, Any]]:
    """Get all meals of a specific type."""
    return [m for m in meals if m.get("meal_type") == meal_type]


def get_meals_by_equipment(
    meals: List[Dict[str, Any]],
    equipment: List[str]
) -> List[Dict[str, Any]]:
    """Get meals that can be made with available equipment."""
    available = set(e.lower() for e in equipment)
    scored = []
    for m in meals:
        required = set(e.lower() for e in m.get("equipment", []))
        if not required or required <= available:
            scored.append((1.0, m))  # Perfect match
        elif required and len(required & available) > 0:
            # Partial match
            score = len(required & available) / len(required)
            scored.append((score, m))
        else:
            scored.append((0.0, m))  # No match
    scored.sort(key=lambda x: x[0], reverse=True)
    return [m for _, m in scored]


def get_meals_by_tag(
    meals: List[Dict[str, Any]],
    tag: str
) -> List[Dict[str, Any]]:
    """Get all meals containing a specific tag."""
    return [m for m in meals if tag in m.get("tags", [])]


def get_all_tags(meals: List[Dict[str, Any]]) -> List[str]:
    """Get all unique tags from meal database."""
    tags = set()
    for m in meals:
        tags.update(m.get("tags", []))
    return sorted(tags)
