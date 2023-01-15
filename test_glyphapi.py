from glyphapi import app
import pytest

# Endpoints

getThresholdEndpoint = "/threshold"
rarityProbabilityCalculatorEndpoint = "/rarityProbabilityCalculator"
effectCountProbabilityCalculatorEndpoint = "effectCountProbabilityCalclulator"

# Test inputs defined here

outOfRangeRequest = { "rarity": 120 }
getThresholdGarbageRequest = { "rarity": "garbage" }
validGlyphThresholdInputRequest = { "rarity": 0 }

rarityProbabilityCalculatorGarbageRequest_test_inputs = [ 
    { "bonus": "garbage" }, 
    { "rarity": "garbage"}, 
    { "rarity" : "-5" }, 
    { "rarity" : "120" },
    ]

impossibleProbabilityRequests = [
  {
   "bonus": "0",
   "ru16": "true", 
   "ru17": "true",
   "rarity": "100",
   "level": "5",
   "numberOfEffects": "4",
  },
  {
   "bonus": "0",
   "ru16": "false", 
   "ru17": "false",
   "rarity": "0",
   "level": "5",
   "numberOfEffects": "3",
  },
  {
   "bonus": "0",
   "ru16": "true", 
   "ru17": "true",
   "rarity": "100",
   "level": "5000",
   "numberOfEffects": "1",
  },
]

nearlyImpossibleProbabilityRequest = {
   "bonus": "0",
   "ru16": "false", 
   "ru17": "false",
   "rarity": "100",
   "level": "1",
}

validProbabilityRarityCalculatorRequest = [
    ({
        "bonus": "0",
        "ru16": "true", 
        "rarity": "100",
    }, 0.03),
    ({
        "ru16": True,
        "bonus": 44,
        "rarity": 100
    }, 11.68)
]

belowMinimumRarityRequests = [
    ({
        "rarity": "0",
        "level": "20",
        "ru16": "true"
    },
    12.0
    ),
    ({
        "ru16": "true",
        "bonus": "10",
        "rarity": "11"
    }, 
    "22.0"
    ),
    ({
        "rarity": "0",
        "level": "20",
        "bonus": "100"
    },
    100.0
    )
]

divisionByZeroCases = [
   ({
   "ru17": "true",
   "rarity": "0",
   "level": "10000",
   "numberOfEffects": "2",
   }, "You have a 50/50 chance of getting 2 or 3 effects."),
   ({
   "ru17": "false",
   "rarity": "0",
   "level": "10000",
   "numberOfEffects": "5",
   "isEffarig": "true" 
   }, "You can only get two effects at this level.")
]

fourEffectsTestCases = [
    ({
   "ru17": "true",
   "rarity": "40",
   "level": "7500",
   "numberOfEffects": "4",
   "isEffarig": "false",
   }, "16.19"),
    ({
   "ru17": "true",
   "rarity": "100",
   "level": "25000",
   "numberOfEffects": "7",
   "isEffarig": "true",
   }, "51.67")
]

effectCountTestCases = [
   ({
   "ru17": "false",
   "rarity": "40",
   "level": "5",
   "numberOfEffects": "2",
   }, "34.21"),
   ({
   "ru17": True,
   "rarity": "100",
   "level": "30000",
   "numberOfEffects": "7", 
   "isEffarig": True  
   }, "56.14"),
   ({
   "ru17": "true",
   "rarity": "40",
   "level": "5",
   "numberOfEffects": "2",
   }, "50.0"),
   ({
   "ru17": "true",
   "rarity": "40",
   "level": "5",
   "numberOfEffects": "1",
   }, "32.89"),
   ({
   "ru17": "true",
   "rarity": "40",
   "level": "5",
   "numberOfEffects": "3",
   }, "17.11"),
   ({
   "ru17": "false",
   "rarity": "40",
   "level": "7500",
   "numberOfEffects": "3",
   }, "23.23"),
   ({
   "ru17": "true",
   "rarity": "40",
   "level": "7500",
   "numberOfEffects": "3",
   }, "47.71"),
]

effectCountGarbageInputs = [
    {
        "level": -5,
        "rarity": 50,
        "numberOfEffects": 2
    },
    {
        "level": 5,
        "rarity": -50,
        "numberOfEffects": 2
    },
    {
        "level": 5,
        "rarity": 500,
        "numberOfEffects": 2
    },
    {
        "level": 5,
        "rarity": 50,
        "numberOfEffects": 8
    },
    {
        "level": "garbage",
        "rarity": 50,
        "numberOfEffects": 2
    },
    {
        "level": 5,
        "rarity": "garbage",
        "numberOfEffects": 2
    },
    {
        "level": 5,
        "rarity": 50,
        "numberOfEffects": "garbage"
    }
]
# Test methods defined here

effectCountMissingInputTestCases = [
    {
        "level": 1,
        "rarity": 2
    },
    {
        "numberOfEffects": 1,
        "rarity": 2
    },
    {
        "level": 1,
        "numberOfEffects": 2
    }
]
def test_getThreshold_outOfRange():
    response = app.test_client().post(getThresholdEndpoint, json = outOfRangeRequest)
    assert response.json["status"] == "Invalid input, must be a number between 0 and 100."

def test_getThreshold_garbageInput():
    response = app.test_client().post(getThresholdEndpoint, json = getThresholdGarbageRequest)
    assert response.json["status"] == "Invalid input, must be a number such as 85.3."

def test_getThreshold_validRequest():
    response = app.test_client().post(getThresholdEndpoint, json = validGlyphThresholdInputRequest)
    assert response.json["status"] == "Guaranteed two effect glyph at level: 10000"

def test_calculateRarityProbability_nearlyImpossibleGlyph():
    response = app.test_client().post(rarityProbabilityCalculatorEndpoint, json = nearlyImpossibleProbabilityRequest)
    assert response.json["status"] == "A glyph with the given rarity would have a probability below 0.01%."

def test_calculateRarityProbability_missingInput():
    response = app.test_client().post(rarityProbabilityCalculatorEndpoint, json = { "level": "1" })
    assert response.json["status"] == "Minimum rarity must be specified."

@pytest.mark.parametrize("test_input, expected_value", validProbabilityRarityCalculatorRequest)
def test_calculateRarityProbability_validRequest(test_input, expected_value):
    response = app.test_client().post(rarityProbabilityCalculatorEndpoint, json = test_input)
    assert response.json["status"] == f"A glyph with the given rarity, or better, would have a probability of {expected_value}%."

@pytest.mark.parametrize("test_input, expected_minimumRarity", belowMinimumRarityRequests)
def test_calculateRarityProbability_belowMinimumRarity(test_input, expected_minimumRarity):
    response = app.test_client().post(rarityProbabilityCalculatorEndpoint, json = test_input)
    assert response.json["status"] == f"The given rarity would be impossible, however you are guaranteed a better rarity of {expected_minimumRarity}%"

@pytest.mark.parametrize("test_input", rarityProbabilityCalculatorGarbageRequest_test_inputs)
def test_calculateRarityProbability_garbageInput(test_input):
    response = app.test_client().post(rarityProbabilityCalculatorEndpoint, json = test_input)
    assert response.json["status"] == "One or more inputs were invalid, please check and try again."

def test_calculateEffectCountProbability_invalidEffectCount():
    response = app.test_client().post(effectCountProbabilityCalculatorEndpoint, json = { "level": 5, "rarity": 50, "numberOfEffects": 5})
    assert response.json["status"] == "You cannot get the specified number of effects on this type of glyph, consider checking your input."

@pytest.mark.parametrize("test_input", impossibleProbabilityRequests)
def test_calculateEffectCountProbability_impossibleGlyph(test_input):
    response = app.test_client().post(effectCountProbabilityCalculatorEndpoint, json = test_input)
    assert response.json["status"] == "A glyph with the given rarity would be impossible."

@pytest.mark.parametrize("test_input, expected_response", divisionByZeroCases)
def test_calculateEffectCountProbability_divisionByZero(test_input, expected_response):
    response = app.test_client().post(effectCountProbabilityCalculatorEndpoint, json = test_input)
    assert response.json["status"] == expected_response

@pytest.mark.parametrize("test_input, expected_value", fourEffectsTestCases)
def testCalculateEffectCountProbability_fourEffects(test_input, expected_value):
    response = app.test_client().post(effectCountProbabilityCalculatorEndpoint, json = test_input)
    assert response.json["status"] == f"The probability of finding a glyph with the given rarity and the number of given effects is {expected_value}%."

@pytest.mark.parametrize("test_input, expected_value", effectCountTestCases)
def test_calculateEffectCountProbability_validRequestTests(test_input, expected_value):
    response = app.test_client().post(effectCountProbabilityCalculatorEndpoint, json = test_input)
    assert response.json["status"] == f"The probability of finding a glyph with the given rarity and the number of given effects is {expected_value}%."

@pytest.mark.parametrize("test_input", effectCountGarbageInputs)
def test_effectCount_garbageInput(test_input):
    response = app.test_client().post(effectCountProbabilityCalculatorEndpoint, json = test_input)
    assert response.json["status"] == "One or more inputs were invalid, please check and try again."

@pytest.mark.parametrize("test_input", effectCountMissingInputTestCases)
def test_effectCount_missingRequiredInputs(test_input):
    response = app.test_client().post(effectCountProbabilityCalculatorEndpoint, json = test_input)
    assert response.json["status"] == "Minimum rarity, target level and effect count must be specified."
