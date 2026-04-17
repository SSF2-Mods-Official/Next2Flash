// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//SSF2API

package 
{
    import flash.display.MovieClip;
    import flash.geom.Point;
    import flash.display.BitmapData;

    public class SSF2API 
    {

        public static const VERSION_MAJOR:int = 0;
        public static const VERSION_MINOR:int = 56;
        public static const VERSION_REVISION:int = 0;
        public static const BASE_CLASSES:Object = {
            "SSF2GameObject":SSF2GameObject,
            "SSF2Character":SSF2Character,
            "SSF2Enemy":SSF2Enemy,
            "SSF2Item":SSF2Item,
            "SSF2Platform":SSF2Platform,
            "SSF2Projectile":SSF2Projectile,
            "SSF2Stage":SSF2Stage,
            "SSF2Platform":SSF2Platform,
            "SSF2CollisionBoundary":SSF2CollisionBoundary,
            "SSF2Target":SSF2Target,
            "SSF2CustomMatch":SSF2CustomMatch,
            "SSF2CustomMode":SSF2CustomMode,
            "SSF2Camera":SSF2Camera,
            "SSF2GameTimer":SSF2GameTimer,
            "SSF2Beacon":SSF2Beacon
        };

        private static var m_api:*;


        public static function init(_arg_1:*):Class
        {
            if (m_api)
            {
                return (SSF2API);
            };
            m_api = _arg_1;
            return (SSF2API);
        }

        public static function deinit():void
        {
            m_api = null;
        }

        public static function signal(_arg_1:int, _arg_2:Object=null):void
        {
            if (!isReady())
            {
                return;
            };
            m_api.signal(_arg_1, _arg_2);
        }

        public static function getAPIVersion():String
        {
            return ("0.56.0");
        }

        public static function print(_arg_1:String):void
        {
            m_api.print(_arg_1);
        }

        public static function getProp(_arg_1:String):*
        {
            return (SSF2Asset.instance.getProp(_arg_1));
        }

        public static function getUID():int
        {
            SSF2API.print("Warning!! SSF2API.getUID() is deprecated. Please use generateUID() instead");
            return (m_api.getUID());
        }

        public static function getCharacter(_arg_1:*):*
        {
            if ((_arg_1 is MovieClip))
            {
                MovieClip(_arg_1).stop();
            };
            if (!isReady())
            {
                return (null);
            };
            return (m_api.getCharacter(_arg_1));
        }

        public static function getCharacters():Array
        {
            if (!isReady())
            {
                return ([]);
            };
            return (m_api.getCharacters());
        }

        public static function getPlayer(_arg_1:*):*
        {
            if ((_arg_1 is MovieClip))
            {
                MovieClip(_arg_1).stop();
            };
            if (!isReady())
            {
                return (null);
            };
            return (m_api.getPlayer(_arg_1));
        }

        public static function getPlayers():Array
        {
            if (!isReady())
            {
                return ([]);
            };
            return (m_api.getPlayers());
        }

        public static function getProjectile(_arg_1:*):*
        {
            if ((_arg_1 is MovieClip))
            {
                MovieClip(_arg_1).stop();
            };
            if (!isReady())
            {
                return (null);
            };
            return (m_api.getProjectile(_arg_1));
        }

        public static function getProjectiles():Array
        {
            if (!isReady())
            {
                return ([]);
            };
            return (m_api.getProjectiles());
        }

        public static function getItem(_arg_1:*):*
        {
            if ((_arg_1 is MovieClip))
            {
                MovieClip(_arg_1).stop();
            };
            if (!isReady())
            {
                return (null);
            };
            return (m_api.getItem(_arg_1));
        }

        public static function getItems():Array
        {
            if (!isReady())
            {
                return ([]);
            };
            return (m_api.getItems());
        }

        public static function getEnemy(_arg_1:*):*
        {
            if ((_arg_1 is MovieClip))
            {
                MovieClip(_arg_1).stop();
            };
            if (!isReady())
            {
                return (null);
            };
            return (m_api.getEnemy(_arg_1));
        }

        public static function getEnemies():Array
        {
            if (!isReady())
            {
                return ([]);
            };
            return (m_api.getEnemies());
        }

        public static function getTarget(_arg_1:*):*
        {
            if ((_arg_1 is MovieClip))
            {
                MovieClip(_arg_1).stop();
            };
            if (!isReady())
            {
                return (null);
            };
            return (m_api.getTarget(_arg_1));
        }

        public static function getTargets():Array
        {
            if (!isReady())
            {
                return ([]);
            };
            return (m_api.getTargets());
        }

        public static function getStage():*
        {
            if (!isReady())
            {
                return (null);
            };
            return (m_api.getStage());
        }

        public static function getCollisionBoundary(_arg_1:*):*
        {
            if (!isReady())
            {
                return (null);
            };
            return (m_api.getCollisionBoundary(_arg_1));
        }

        public static function getPlatform(_arg_1:*):*
        {
            if (!isReady())
            {
                return (null);
            };
            return (m_api.getPlatform(_arg_1));
        }

        public static function getPlatforms(_arg_1:Object=null):Array
        {
            if (!isReady())
            {
                return ([]);
            };
            return (m_api.getPlatforms(_arg_1));
        }

        public static function getPlatformBetweenPoints(_arg_1:Point, _arg_2:Point, _arg_3:Object=null):*
        {
            if (!isReady())
            {
                return (null);
            };
            return (m_api.getPlatformBetweenPoints(_arg_1, _arg_2, _arg_3));
        }

        public static function getCamBounds():MovieClip
        {
            SSF2API.print("Warning!! SSF2API.getCamBounds() is deprecated. Please use SSF2API.getStage().getCameraBounds() instead");
            if (!isReady())
            {
                return (null);
            };
            return (m_api.getCamBounds());
        }

        public static function getDeathBounds():MovieClip
        {
            SSF2API.print("Warning!! SSF2API.getDeathBounds() is deprecated. Please use SSF2API.getStage().getDeathBounds() instead");
            if (!isReady())
            {
                return (null);
            };
            return (m_api.getDeathBounds());
        }

        public static function hitTestGround(_arg_1:Number, _arg_2:Number, _arg_3:Object=null):*
        {
            if (!isReady())
            {
                return (null);
            };
            return (m_api.hitTestGround(_arg_1, _arg_2, _arg_3));
        }

        public static function hitTestGroundBetweenPoints(_arg_1:Point, _arg_2:Point, _arg_3:Object=null):*
        {
            if (!isReady())
            {
                return (null);
            };
            return (m_api.hitTestGroundBetweenPoints(_arg_1, _arg_2, _arg_3));
        }

        public static function lightFlash(_arg_1:Boolean=true):void
        {
            SSF2API.print("Warning!! SSF2API.lightFlash() is deprecated. Please use SSF2API.getCamera().lightFlash() instead");
            if (!isReady())
            {
                return;
            };
            m_api.lightFlash(_arg_1);
        }

        public static function setCamStageFocus(_arg_1:int):void
        {
            SSF2API.print("Warning!! SSF2API.setCamStageFocus() is deprecated. Please use SSF2API.getCamera().setCamStageFocus() instead");
            if (!isReady())
            {
                return;
            };
            m_api.setCamStageFocus(_arg_1);
        }

        public static function removeCamStageFocus():void
        {
            SSF2API.print("Warning!! SSF2API.removeCamStageFocus() is deprecated. Please use SSF2API.getCamera().removeCamStageFocus() instead");
            if (!isReady())
            {
                return;
            };
            m_api.removeCamStageFocus();
        }

        public static function addEventListener(_arg_1:String, _arg_2:Function, _arg_3:Object=null):void
        {
            if (!isReady())
            {
                return;
            };
            m_api.addEventListener(_arg_1, _arg_2, _arg_3);
        }

        public static function hasEventListener(_arg_1:String, _arg_2:Function=null):Boolean
        {
            if (!isReady())
            {
                return (false);
            };
            return (m_api.hasEventListener(_arg_1, _arg_2));
        }

        public static function removeEventListener(_arg_1:String, _arg_2:Function):void
        {
            if (!isReady())
            {
                return;
            };
            m_api.removeEventListener(_arg_1, _arg_2);
        }

        public static function playSound(_arg_1:*, _arg_2:Boolean=false):int
        {
            return (m_api.playSound(_arg_1, _arg_2));
        }

        public static function stopSound(_arg_1:int):void
        {
            m_api.stopSound(_arg_1);
        }

        public static function playMusic(_arg_1:String, _arg_2:int):void
        {
            m_api.playMusic(_arg_1, _arg_2);
        }

        public static function stopMusic():void
        {
            m_api.stopMusic();
        }

        public static function getCurrentMusicInfo():Object
        {
            return (m_api.getCurrentMusicInfo());
        }

        public static function shakeCamera(_arg_1:int):void
        {
            SSF2API.print("Warning!! SSF2API.shakeCamera() is deprecated. Please use SSF2API.getCamera().shake() instead");
            if (!isReady())
            {
                return;
            };
            m_api.shakeCamera(_arg_1);
        }

        public static function matchGo():void
        {
            if (!isReady())
            {
                return;
            };
            m_api.matchGo();
        }

        public static function matchGoComplete():void
        {
            if (!isReady())
            {
                return;
            };
            m_api.matchGoComplete();
        }

        public static function random():Number
        {
            if (!isReady())
            {
                return (0);
            };
            return (m_api.random());
        }

        public static function randomInteger(_arg_1:int, _arg_2:int):int
        {
            if (!isReady())
            {
                return (0);
            };
            return (m_api.randomInteger(_arg_1, _arg_2));
        }

        public static function safeRandom():Number
        {
            if (!isReady())
            {
                return (0);
            };
            return (m_api.safeRandom());
        }

        public static function safeRandomInteger(_arg_1:int, _arg_2:int):int
        {
            if (!isReady())
            {
                return (0);
            };
            return (m_api.safeRandomInteger(_arg_1, _arg_2));
        }

        public static function fixBG():void
        {
            if (!isReady())
            {
                return;
            };
            m_api.fixBG();
        }

        public static function attachEffect(_arg_1:*, _arg_2:Object=null):MovieClip
        {
            if (!isReady())
            {
                return (null);
            };
            return (m_api.attachEffect(_arg_1, _arg_2));
        }

        public static function attachEffectOverlay(_arg_1:*, _arg_2:Object=null):MovieClip
        {
            if (!isReady())
            {
                return (null);
            };
            return (m_api.attachEffectOverlay(_arg_1, _arg_2));
        }

        public static function calculateChargeDamage(_arg_1:Object):Number
        {
            if (!isReady())
            {
                return (0);
            };
            return (m_api.calculateChargeDamage(_arg_1));
        }

        public static function calculateSelfHitStun(_arg_1:Number, _arg_2:Number):Number
        {
            if (!isReady())
            {
                return (0);
            };
            return (m_api.calculateSelfHitStun(_arg_1, _arg_2));
        }

        public static function calculateKnockback(_arg_1:Number, _arg_2:Number, _arg_3:Number, _arg_4:Number, _arg_5:Number, _arg_6:Number, _arg_7:Boolean):Number
        {
            return (m_api.calculateKnockback(_arg_1, _arg_2, _arg_3, _arg_4, _arg_5, _arg_6, _arg_7));
        }

        public static function calculateKnockbackVelocity(_arg_1:Number):Number
        {
            return (m_api.calculateKnockbackVelocity(_arg_1));
        }

        public static function getTimestamp():Date
        {
            if (!isReady())
            {
                return (null);
            };
            return (m_api.getTimestamp());
        }

        public static function getElapsedFrames():int
        {
            if (!isReady())
            {
                return (0);
            };
            return (m_api.getElapsedFrames());
        }

        public static function isHazardsOn():Boolean
        {
            if (!isReady())
            {
                return (false);
            };
            return (m_api.isHazardsOn());
        }

        public static function generateItem(_arg_1:String, _arg_2:Number, _arg_3:Number, _arg_4:Boolean=false):*
        {
            if (!isReady())
            {
                return (null);
            };
            return (m_api.generateItem(_arg_1, _arg_2, _arg_3, _arg_4));
        }

        public static function getRandomAssist():Class
        {
            if (!isReady())
            {
                return (null);
            };
            return (m_api.getRandomAssist());
        }

        public static function getRandomPokemon():Class
        {
            if (!isReady())
            {
                return (null);
            };
            return (m_api.getRandomPokemon());
        }

        public static function spawnAssist(_arg_1:Class, _arg_2:*=null):*
        {
            if (!isReady())
            {
                return (null);
            };
            return (m_api.spawnAssist(_arg_1, _arg_2));
        }

        public static function spawnPokemon(_arg_1:Class, _arg_2:*=null):*
        {
            if (!isReady())
            {
                return (null);
            };
            return (m_api.spawnPokemon(_arg_1, _arg_2));
        }

        public static function spawnCharacter(_arg_1:Class):*
        {
            return (m_api.spawnCharacter(_arg_1));
        }

        public static function spawnEnemy(_arg_1:*):*
        {
            return (m_api.spawnEnemy(_arg_1));
        }

        public static function spawnItem(_arg_1:Class):*
        {
            return (m_api.spawnItem(_arg_1));
        }

        public static function spawnProjectile(_arg_1:Class, _arg_2:*=null):*
        {
            return (m_api.spawnProjectile(_arg_1, _arg_2));
        }

        public static function spawnCollisionBoundary(_arg_1:Class):*
        {
            if (!isReady())
            {
                return (null);
            };
            return (m_api.spawnCollisionBoundary(_arg_1));
        }

        public static function spawnPlatform(_arg_1:Class, _arg_2:Boolean=true):*
        {
            if (!isReady())
            {
                return (null);
            };
            return (m_api.spawnPlatform(_arg_1, _arg_2));
        }

        public static function isReady():Boolean
        {
            return ((m_api) && (m_api.isReady()));
        }

        public static function hitboxTest(_arg_1:*, _arg_2:uint, _arg_3:*, _arg_4:uint):Array
        {
            return (m_api.hitboxTest(_arg_1, _arg_2, _arg_3, _arg_4));
        }

        public static function getQualitySettings():Object
        {
            if (!isReady())
            {
                return (null);
            };
            return (m_api.getQualitySettings());
        }

        public static function currentActiveFinalSmash():*
        {
            if (!isReady())
            {
                return (null);
            };
            return (m_api.currentActiveFinalSmash());
        }

        public static function getSmashBallInstance():*
        {
            if (!isReady())
            {
                return (null);
            };
            return (m_api.getSmashBallInstance());
        }

        public static function enableSmashBallSpawn(_arg_1:Boolean):void
        {
            if (!isReady())
            {
                return;
            };
            m_api.enableSmashBallSpawn(_arg_1);
        }

        public static function isSmashBallSpawnEnabled():Boolean
        {
            if (!isReady())
            {
                return (false);
            };
            return (m_api.isSmashBallSpawnEnabled());
        }

        public static function isDebug():Boolean
        {
            if (!isReady())
            {
                return (false);
            };
            return (m_api.isDebug());
        }

        public static function addHUDDetection(_arg_1:MovieClip):void
        {
            if (!isReady())
            {
                return;
            };
            m_api.addHUDDetection(_arg_1);
        }

        public static function removeHUDDetection(_arg_1:MovieClip):void
        {
            if (!isReady())
            {
                return;
            };
            m_api.removeHUDDetection(_arg_1);
        }

        public static function addTimedCameraTarget(_arg_1:*, _arg_2:int):void
        {
            SSF2API.print("Warning!! SSF2API.addTimedCameraTarget() is deprecated. Please use SSF2API.getCamera().addTimedTarget() instead");
            if (!isReady())
            {
                return;
            };
            m_api.addTimedCameraTarget(_arg_1, _arg_2);
        }

        public static function removeTimedCameraTarget(_arg_1:*):void
        {
            SSF2API.print("Warning!! SSF2API.removeTimedCameraTarget() is deprecated. Please use SSF2API.getCamera().deleteTimedTarget() instead");
            if (!isReady())
            {
                return;
            };
            m_api.removeTimedCameraTarget(_arg_1);
        }

        public static function hasFeature(_arg_1:uint):Boolean
        {
            if (!isReady())
            {
                return (false);
            };
            return (m_api.hasFeature(_arg_1));
        }

        public static function getItemFrequency():int
        {
            if (!isReady())
            {
                return (0);
            };
            return (m_api.getItemFrequency());
        }

        public static function setItemFrequency(_arg_1:Number):void
        {
            if (!isReady())
            {
                return;
            };
            m_api.setItemFrequency(_arg_1);
        }

        public static function addCustomItem(_arg_1:Object):void
        {
            if (!isReady())
            {
                return;
            };
            m_api.addCustomItem(_arg_1);
        }

        public static function getAvailableItemList():Array
        {
            if (!isReady())
            {
                return ([]);
            };
            return (m_api.getAvailableItemList());
        }

        public static function getMatchSettings():Object
        {
            if (!isReady())
            {
                return (null);
            };
            return (m_api.getMatchSettings());
        }

        public static function getGameSettings():Object
        {
            if (!isReady())
            {
                return (null);
            };
            return (m_api.getGameSettings());
        }

        public static function generateUID():int
        {
            if (!isReady())
            {
                return (0);
            };
            return (m_api.generateUID());
        }

        public static function getRandomItemSpawnLocation():Point
        {
            if (!isReady())
            {
                return (null);
            };
            return (m_api.getRandomItemSpawnLocation());
        }

        public static function isFSCutscenePlaying():Boolean
        {
            if (!isReady())
            {
                return (false);
            };
            return (m_api.isFSCutscenePlaying());
        }

        public static function isGameEnded():Boolean
        {
            if (!isReady())
            {
                return (false);
            };
            return (m_api.isGameEnded());
        }

        public static function getRandomCharacterID(_arg_1:Boolean=true):String
        {
            return (m_api.getRandomCharacterID(_arg_1));
        }

        public static function getRandomStageID(_arg_1:Boolean=true, _arg_2:Boolean=true):String
        {
            return (m_api.getRandomStageID(_arg_1, _arg_2));
        }

        public static function createCustomMatch(_arg_1:Class, _arg_2:SSF2CustomMode, _arg_3:Object):SSF2CustomMatch
        {
            return (m_api.createCustomMatch(_arg_1, _arg_2, _arg_3));
        }

        public static function createCustomMenu(_arg_1:Class):*
        {
            return (m_api.createCustomMenu(_arg_1));
        }

        public static function endGame(_arg_1:Object=null):void
        {
            m_api.endGame(_arg_1);
        }

        public static function getMCByLinkageName(_arg_1:String):MovieClip
        {
            return (m_api.getMCByLinkageName(_arg_1));
        }

        public static function getCharacterStats(_arg_1:String):Object
        {
            return (m_api.getCharacterStats(_arg_1));
        }

        public static function queueResources(_arg_1:Array):void
        {
            m_api.queueResources(_arg_1);
        }

        public static function loadResources(_arg_1:Object):void
        {
            m_api.loadResources(_arg_1);
        }

        public static function getGameTimer():*
        {
            return (m_api.getGameTimer());
        }

        public static function getCamera():*
        {
            return (m_api.getCamera());
        }

        public static function freezeInputs(_arg_1:Boolean):void
        {
            m_api.freezeInputs(_arg_1);
        }

        public static function getItemStatsList(_arg_1:Boolean=true, _arg_2:Boolean=true):Array
        {
            return (m_api.getItemStatsList(_arg_1, _arg_2));
        }

        public static function getRandomItemStats(_arg_1:Boolean=true, _arg_2:Boolean=true):Object
        {
            return (m_api.getRandomItemStats(_arg_1, _arg_2));
        }

        public static function getAverageFPS():Number
        {
            if (!isReady())
            {
                return (0);
            };
            return (m_api.getAverageFPS());
        }

        public static function setFrameRate(_arg_1:Number):void
        {
            m_api.setFrameRate(_arg_1);
        }

        public static function getAssistTrophyStatsList(_arg_1:String="common"):Array
        {
            return (m_api.getAssistTrophyStatsList(_arg_1));
        }

        public static function getPokemonStatsList(_arg_1:String="common"):Array
        {
            return (m_api.getPokemonStatsList(_arg_1));
        }

        public static function getGlobalVar(_arg_1:String):*
        {
            return (m_api.getGlobalVar(_arg_1));
        }

        public static function setGlobalVar(_arg_1:String, _arg_2:*):void
        {
            m_api.setGlobalVar(_arg_1, _arg_2);
        }

        public static function getSnapshot(_arg_1:Object=null):BitmapData
        {
            return (m_api.getSnapshot(_arg_1));
        }

        public static function getTargetTestSaveData(_arg_1:String, _arg_2:String):Object
        {
            return (m_api.getTargetTestSaveData(_arg_1, _arg_2));
        }

        public static function getManifest():Object
        {
            return (m_api.getManifest());
        }

        public static function isGameStarted():Boolean
        {
            if (!isReady())
            {
                return (false);
            };
            return (!(m_api.isGameStarted()));
        }

        public static function getCustomMode():*
        {
            if (!isReady())
            {
                return (null);
            };
            return (m_api.getCustomMode());
        }

        public static function getGameMode():int
        {
            return (m_api.getGameMode());
        }

        public static function getCustomMatch():*
        {
            if (!isReady())
            {
                return (null);
            };
            return (m_api.getCustomMatch());
        }

        public static function getUnlockableData():Object
        {
            return (m_api.getUnlockableData());
        }

        public static function triggerUnlock(_arg_1:String):Boolean
        {
            return (m_api.triggerUnlock(_arg_1));
        }

        public static function getCostumeData(_arg_1:String, _arg_2:int, _arg_3:int=-1):Object
        {
            return (m_api.getCostumeData(_arg_1, _arg_2, _arg_3));
        }

        public static function getMetalCostume(_arg_1:String):Object
        {
            return (m_api.getMetalCostume(_arg_1));
        }

        public static function getWinners():Array
        {
            return (m_api.getWinners());
        }

        public static function getLosers():Array
        {
            return (m_api.getLosers());
        }


    }
}//package 

