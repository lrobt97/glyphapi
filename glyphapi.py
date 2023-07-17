from flask import Flask
from flask import request, jsonify
import numpy
from scipy.stats import norm
app = Flask(__name__)

# Request Object:
# {
#   rarity: float (required)
# }
#
# Response:
# {
#   status: string
# }
@app.route("/threshold", methods=["POST"])
def getThreshold():
    rarity = request.get_json()['rarity']
    try:
        rarity = float(rarity)
    except:
        response = {"status" : "Invalid input, must be a number such as 85.3."}
        return jsonify(response)
    if rarity > 100 or rarity < 0:
        response = { "status": "Invalid input, must be a number between 0 and 100."}
        return jsonify(response)
    else:
        response = {"status": "Guaranteed two effect glyph at level: " + str(numpy.int32(numpy.ceil(100**2/(2.5 * rarity /100 + 1 ))))}
        return jsonify(response)

# Request Object:
# {
#   bonus: float (optional, default: 0)
#   ru16: boolean (optional, default: true)
#   rarity: float (required)
#  }
#
# Response:
# {
#   status: string
# }
@app.route("/rarityProbabilityCalculator", methods = ["POST"])
def calculateRarityProbability():
    input = request.get_json()
    bonus = 0
    rarity = 0
    ru16 = True
    try:
        if "bonus" in input:
            bonus = float(input["bonus"])

        if "rarity" not in input:
            return { "status": "Minimum rarity must be specified." }

        rarity = float(input["rarity"])

        if rarity < 0 or rarity > 100:
            return { "status": "One or more inputs were invalid, please check and try again." }   

        if "ru16" in input:
            ru16 = input["ru16"]    

    except:
        return { "status": "One or more inputs were invalid, please check and try again." }
    
    # The minimum value a normally distributed variable would need to be for the required rarity
    minimumStrength = 2.5 * rarity / 100 + 1 - bonus
    if ru16:
        minimumStrength /= 1.3

    # The theoretical minimum rarity that could be generated
    theoreticalMinimum = numpy.min([1.3 + bonus/40, 3.5]) if ru16 else numpy.min([1 + bonus/40, 3.5])


    if minimumStrength < theoreticalMinimum:
        theoreticalMinimumRarity = numpy.round(numpy.ceil(400*((theoreticalMinimum - 1) * 100 / 2.5)) / 400, 1)
        return { "status": f"The given rarity would be impossible, however you are guaranteed a better rarity of {theoreticalMinimumRarity}%"}
    
    z = minimumStrength ** (1 / 0.65) - 1
    probabilityOfRarity = 2 * (1 - norm.cdf(z))
    probabilityOfRarity = numpy.round(probabilityOfRarity * 100, 2)
    if probabilityOfRarity < 0.01:
        return { "status": "A glyph with the given rarity would have a probability below 0.01%." }
    else:
        return { "status": f"A glyph with the given rarity, or better, would have a probability of {probabilityOfRarity}%." }

# Request Object:
# {
#   ru17: boolean (optional, default: true)
#   rarity: float (required)
#   level: int (required)
#   numberOfEffects: int (required)
#   isEffarig: boolean (optional, default: false)
#  }
#
# Response:
# {
#   status: string
# }
#
# Note: this method is agnostic to any logic involving minimum glyph rarity thresholds
@app.route("/effectCountProbabilityCalclulator", methods = ["POST"])
def calculateEffectCountProbability():
    input = request.get_json()
    ru17 = True
    isEffarig = False
    probabilityOfEffectCount = 0
    try:
        if "rarity" not in input or "level" not in input or "numberOfEffects" not in input:
            return { "status": "Minimum rarity, target level and effect count must be specified." }

        if "isEffarig" in input:
            isEffarig = input["isEffarig"]

        level = int(input["level"])
        rarity = float(input["rarity"])
        numberOfEffects = int(input["numberOfEffects"])
        if level < 0 or rarity < 0 or rarity > 100 or numberOfEffects < 0 or numberOfEffects > 7:
            return { "status": "One or more inputs were invalid, please check and try again." }  

        if (numberOfEffects > 4 and not isEffarig):
            return { "status": "You cannot get the specified number of effects on this type of glyph, consider checking your input."}

        if "ru17" in input:
            ru17 = input["ru17"]

    except:
        return { "status": "One or more inputs were invalid, please check and try again." }

    threshold = numpy.ceil(100**2/(2.5 * rarity /100 + 1 ))
    if (level < threshold and numberOfEffects >= 4) or (level < threshold and numberOfEffects >= 3 and not ru17) or (level > threshold and numberOfEffects == 1):
        return { "status": "A glyph with the given rarity would be impossible." }

    # Above the threshold the random value must be greater than the calculated value, below the threshold
    # the random value must be below the calculated value. 
    strength = 2.5 * rarity / 100 + 1
    if level * strength != 10000:
        if not ru17:
            probabilityOfEffectCount = effectCountProbabilityModel(threshold, strength, level, numberOfEffects, isEffarig)
        else:
            if numberOfEffects == 2 and level > threshold:
                probabilityOfEffectCount = effectCountProbabilityModel(threshold, strength, level, numberOfEffects, isEffarig) * 0.5
            elif level < threshold:
                probabilityOfEffectCount = (1 - 0.5 * (not numberOfEffects == 2)) * effectCountProbabilityModel(threshold, strength, level, numberOfEffects, isEffarig) + 0.5 * effectCountProbabilityModel(threshold, strength, level, numberOfEffects - 1, isEffarig)
            else:
                probabilityOfEffectCount = effectCountProbabilityModel(threshold, strength, level, numberOfEffects, isEffarig) * (1 - 0.5 * ( not ( ( not isEffarig and numberOfEffects == 4 )  or ( isEffarig and numberOfEffects == 7 )) ) ) + effectCountProbabilityModel(threshold, strength, level, numberOfEffects - 1, isEffarig) * 0.5
    else:
        response = "You have a 50/50 chance of getting 2 or 3 effects." if ru17 else "You can only get two effects at this level."
        return { "status":  response }
    probabilityOfEffectCount = numpy.round(probabilityOfEffectCount * 100, 2)
    return {"status": f"The probability of finding a glyph with the given rarity and the number of given effects is {probabilityOfEffectCount}%."}

def effectCountProbabilityModel(threshold, strength, level, effectCount, isEffarig):
        if effectCount <= 0: return 0
        uniformDistributionTargetBounds = [((effectCount - 1) / 1.5) ** (1 / (1 - (level * strength) ** 0.5 / 100)), ((effectCount) / 1.5) ** (1 / (1 - (level * strength) ** 0.5 / 100))]
        if (effectCount == 4 and not isEffarig) or (effectCount == 7 and isEffarig): return numpy.min([uniformDistributionTargetBounds[0], 1])
        if (level < threshold): probabilityOfEffectCount = numpy.max([numpy.min([uniformDistributionTargetBounds[1], 1]) - uniformDistributionTargetBounds[0], 0])
        else: probabilityOfEffectCount = numpy.max([numpy.min([uniformDistributionTargetBounds[0], 1]) - uniformDistributionTargetBounds[1], 0])
        return probabilityOfEffectCount

if __name__ == "__main__":
   app.run(host='0.0.0.0', port=5000)
