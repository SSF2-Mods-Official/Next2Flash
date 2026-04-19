// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//SSF2GameObject

package 
{
    import flash.display.MovieClip;
    import flash.geom.Point;
    import flash.geom.Rectangle;

    public class SSF2GameObject extends SSF2BaseAPIObject 
    {

        public function SSF2GameObject(_arg_1:*):void
        {
            super(_arg_1);
        }

        override public function getType():String
        {
            return ("SSF2GameObject");
        }

        public function getOwnStats():Object
        {
            return ({});
        }

        public function getAttackStats():Object
        {
            return ({});
        }

        public function getProjectileStats():Object
        {
            return ({});
        }

        public function getItemStats():Object
        {
            return ({});
        }

        public function getGameObjectStat(_arg_1:String):*
        {
            return (_api.getGameObjectStat(_arg_1));
        }

        public function playSound(_arg_1:*, _arg_2:Boolean=false):int
        {
            return (_api.playSound(_arg_1, _arg_2));
        }

        public function stopSound(_arg_1:int):void
        {
            _api.stopSound(_arg_1);
        }

        public function addToCamera():void
        {
            _api.addToCamera();
        }

        public function addEventListener(_arg_1:String, _arg_2:Function, _arg_3:Object=null):void
        {
            if ((_arg_1 === "projCollideOwner"))
            {
                SSF2API.print("Warning!! SSF2Event.PROJ_COLLIDE_OWNER event is deprecated, please use PROJ_COLLIDE event instead");
            };
            _api.addEventListener(_arg_1, _arg_2, _arg_3);
        }

        public function hasEventListener(_arg_1:String, _arg_2:Function=null):Boolean
        {
            return (_api.hasEventListener(_arg_1, _arg_2));
        }

        public function removeEventListener(_arg_1:String, _arg_2:Function):void
        {
            _api.removeEventListener(_arg_1, _arg_2);
        }

        public function attachEffect(_arg_1:*, _arg_2:Object=null):MovieClip
        {
            return (_api.attachEffect(_arg_1, _arg_2));
        }

        public function attachEffectOverlay(_arg_1:*, _arg_2:Object=null):MovieClip
        {
            return (_api.attachEffectOverlay(_arg_1, _arg_2));
        }

        public function camFocus(_arg_1:int):void
        {
            _api.camFocus(_arg_1);
        }

        public function camUnfocus():void
        {
            _api.camUnfocus();
        }

        public function createTimer(_arg_1:int, _arg_2:int, _arg_3:Function, _arg_4:Object=null):void
        {
            _api.createTimer(_arg_1, _arg_2, _arg_3, _arg_4);
        }

        public function destroyTimer(_arg_1:Function):void
        {
            _api.destroyTimer(_arg_1);
        }

        public function faceLeft():void
        {
            _api.faceLeft();
        }

        public function faceRight():void
        {
            _api.faceRight();
        }

        public function flip(_arg_1:*=null):void
        {
            _api.flip(_arg_1);
        }

        public function forceHitStun(_arg_1:int, _arg_2:Number=-1):void
        {
            _api.forceHitStun(_arg_1, _arg_2);
        }

        public function getAttackBoxStat(_arg_1:int, _arg_2:String):*
        {
            return (_api.getAttackBoxStat(_arg_1, _arg_2));
        }

        public function exportAttackBoxStats(_arg_1:int, _arg_2:String):Object
        {
            return (_api.exportAttackBoxStats(_arg_1, _arg_2));
        }

        public function getAttackStat(_arg_1:String):*
        {
            return (_api.getAttackStat(_arg_1));
        }

        public function getCounterAttackBoxStats():Object
        {
            return (_api.getCounterAttackBoxStats());
        }

        public function getGlobalVariable(_arg_1:String):*
        {
            return (_api.getGlobalVariable(_arg_1));
        }

        public function getHeight():Number
        {
            return (_api.getHeight());
        }

        public function getHitBox(_arg_1:String):Object
        {
            return (_api.getHitBox(_arg_1));
        }

        public function getHomingTarget():*
        {
            return (_api.getHomingTarget());
        }

        public function getID():int
        {
            return (_api.getID());
        }

        public function getTeamID():int
        {
            return (_api.getTeamID());
        }

        public function setTeamID(_arg_1:int):void
        {
            _api.setTeamID(_arg_1);
        }

        public function getLinkageID():String
        {
            return (_api.getLinkageID());
        }

        public function getMC():MovieClip
        {
            return (_api.getMC());
        }

        public function getProjectiles():Array
        {
            return (_api.getProjectiles());
        }

        public function getRotation():Number
        {
            return (_api.getRotation());
        }

        public function getScale():Point
        {
            return (_api.getScale());
        }

        public function getStanceMC():MovieClip
        {
            return (_api.getStanceMC());
        }

        public function getUID():int
        {
            return (_api.getUID());
        }

        public function getWidth():Number
        {
            return (_api.getWidth());
        }

        public function getX():Number
        {
            return (_api.getX());
        }

        public function getXScale():Number
        {
            return (_api.getXScale());
        }

        public function getXSpeed():Number
        {
            return (_api.getXSpeed());
        }

        public function getY():Number
        {
            return (_api.getY());
        }

        public function getYScale():Number
        {
            return (_api.getYScale());
        }

        public function getYSpeed():Number
        {
            return (_api.getYSpeed());
        }

        public function getNearest(_arg_1:String, _arg_2:Boolean=true, _arg_3:Boolean=true):*
        {
            return (_api.getNearest(_arg_1, _arg_2, _arg_3));
        }

        public function getNearestPath(_arg_1:String, _arg_2:Boolean=true, _arg_3:Boolean=true):Array
        {
            return (_api.getNearestPath(_arg_1, _arg_2, _arg_3));
        }

        public function getNearestLedge():MovieClip
        {
            return (_api.getNearestLedge());
        }

        public function getCurrentPlatform():*
        {
            return (_api.getCurrentPlatform());
        }

        public function homeTowardsTarget(_arg_1:Number, _arg_2:*):void
        {
            _api.homeTowardsTarget(_arg_1, _arg_2);
        }

        public function isFacingRight():Boolean
        {
            return (_api.isFacingRight());
        }

        public function isOnGround():Boolean
        {
            return (_api.isOnGround());
        }

        public function netSpeed(_arg_1:Boolean=false, _arg_2:Boolean=false):Number
        {
            return (_api.netSpeed(_arg_1, _arg_2));
        }

        public function netXSpeed(_arg_1:Boolean=false, _arg_2:Boolean=false):Number
        {
            return (_api.netXSpeed(_arg_1, _arg_2));
        }

        public function netYSpeed(_arg_1:Boolean=false, _arg_2:Boolean=false):Number
        {
            return (_api.netYSpeed(_arg_1, _arg_2));
        }

        public function removeFromCamera():void
        {
            _api.removeFromCamera();
        }

        public function refreshAttackID():void
        {
            _api.refreshAttackID();
        }

        public function refreshStaleID():void
        {
            _api.refreshStaleID();
        }

        public function resetRotation():void
        {
            _api.resetRotation();
        }

        public function resetKnockback():void
        {
            _api.resetKnockback();
        }

        public function resetKnockbackDecay():void
        {
            _api.resetKnockbackDecay();
        }

        public function getKnockbackDecay():Object
        {
            return (_api.getKnockbackDecay());
        }

        public function setKnockbackDecay(_arg_1:Number, _arg_2:Number):void
        {
            _api.setKnockbackDecay(_arg_1, _arg_2);
        }

        public function safeMove(_arg_1:Number, _arg_2:Number):Boolean
        {
            return (_api.safeMove(_arg_1, _arg_2));
        }

        public function setCamBoxSize(_arg_1:Number, _arg_2:Number, _arg_3:Number=0, _arg_4:Number=0):void
        {
            _api.setCamBoxSize(_arg_1, _arg_2, _arg_3, _arg_4);
        }

        public function setGlobalVariable(_arg_1:String, _arg_2:*):void
        {
            _api.setGlobalVariable(_arg_1, _arg_2);
        }

        public function setPosition(_arg_1:Number, _arg_2:Number):void
        {
            _api.setPosition(_arg_1, _arg_2);
        }

        public function setRotation(_arg_1:Number):void
        {
            _api.setRotation(_arg_1);
        }

        public function setScale(_arg_1:Number, _arg_2:Number):void
        {
            _api.setScale(_arg_1, _arg_2);
        }

        public function setX(_arg_1:Number):void
        {
            _api.setX(_arg_1);
        }

        public function setXSpeed(_arg_1:Number, _arg_2:Boolean=true):void
        {
            _api.setXSpeed(_arg_1, _arg_2);
        }

        public function setY(_arg_1:Number):void
        {
            _api.setY(_arg_1);
        }

        public function setYSpeed(_arg_1:Number):void
        {
            _api.setYSpeed(_arg_1);
        }

        public function stancePlayFrame(_arg_1:*):void
        {
            _api.stancePlayFrame(_arg_1);
        }

        public function swapDepths(_arg_1:*):void
        {
            _api.swapDepths(_arg_1);
        }

        public function bringBehind(_arg_1:*):void
        {
            _api.bringBehind(_arg_1);
        }

        public function bringInFront(_arg_1:*):void
        {
            _api.bringInFront(_arg_1);
        }

        public function attachToGround():void
        {
            _api.attachToGround();
        }

        public function unnattachFromGround():void
        {
            _api.unnattachFromGround();
        }

        public function updateAttackBoxStats(_arg_1:int, _arg_2:Object):void
        {
            _api.updateAttackBoxStats(_arg_1, _arg_2);
        }

        public function updateAttackStats(_arg_1:Object):void
        {
            _api.updateAttackStats(_arg_1);
        }

        public function replaceAttackStats(_arg_1:String, _arg_2:Object):void
        {
            _api.replaceAttackStats(_arg_1, _arg_2);
        }

        public function replaceAttackBoxStats(_arg_1:String, _arg_2:int, _arg_3:Object):void
        {
            _api.replaceAttackBoxStats(_arg_1, _arg_2, _arg_3);
        }

        public function inState(_arg_1:uint):Boolean
        {
            return (_api.inState(_arg_1));
        }

        public function getState():uint
        {
            return (_api.getState());
        }

        public function setState(_arg_1:uint):void
        {
            _api.setState(_arg_1);
        }

        public function extraHitTests(_arg_1:Number, _arg_2:Number, _arg_3:*):Boolean
        {
            return (false);
        }

        public function takeDamage(_arg_1:Object, _arg_2:*, _arg_3:Rectangle=null):Boolean
        {
            return (_api.takeDamage(_arg_1, _arg_2, _arg_3));
        }

        public function getBoundsRect():Rectangle
        {
            return (_api.getBoundsRect());
        }

        public function getCurrentAnimation():String
        {
            return (_api.getCurrentAnimation());
        }

        public function getStageParentPosition():Point
        {
            return (_api.getStageParentPosition());
        }

        public function applyKnockback(_arg_1:Number, _arg_2:Number):void
        {
            _api.applyKnockback(_arg_1, _arg_2);
        }

        public function applyKnockbackSpeed(_arg_1:Number, _arg_2:Number):void
        {
            _api.applyKnockbackSpeed(_arg_1, _arg_2);
        }

        public function resetFade(_arg_1:int=15):void
        {
            _api.resetFade(_arg_1);
        }

        public function fadeIn():void
        {
            _api.fadeIn();
        }

        public function fadeOut():void
        {
            _api.fadeOut();
        }

        public function inHitStun():Boolean
        {
            return (_api.inHitStun());
        }

        public function inParalysis():Boolean
        {
            return (_api.inParalysis());
        }

        public function inLowerLeftWarningBounds():Boolean
        {
            return (_api.inLowerLeftWarningBounds());
        }

        public function inUpperLeftWarningBounds():Boolean
        {
            return (_api.inUpperLeftWarningBounds());
        }

        public function inLowerRightWarningBounds():Boolean
        {
            return (_api.inLowerRightWarningBounds());
        }

        public function inUpperRightWarningBounds():Boolean
        {
            return (_api.inUpperRightWarningBounds());
        }

        public function setTargetInterrupt(_arg_1:Function):void
        {
            _api.setTargetInterrupt(_arg_1);
        }

        public function createSelfPlatform(_arg_1:Number, _arg_2:Number, _arg_3:Number, _arg_4:Number, _arg_5:Boolean=true):*
        {
            return (_api.createSelfPlatform(_arg_1, _arg_2, _arg_3, _arg_4, _arg_5, SSF2Platform));
        }

        public function createSelfPlatformWithMC(_arg_1:MovieClip, _arg_2:Boolean=true):*
        {
            return (_api.createSelfPlatformWithMC(_arg_1, _arg_2, SSF2Platform));
        }

        public function removeSelfPlatform():void
        {
            _api.removeSelfPlatform();
        }

        public function getDamage():Number
        {
            return (_api.getDamage());
        }

        public function setDamage(_arg_1:Number):void
        {
            _api.setDamage(_arg_1);
        }

        public function dealDamage(_arg_1:Number):void
        {
            _api.dealDamage(_arg_1);
        }

        public function healDamage(_arg_1:Number):void
        {
            _api.healDamage(_arg_1);
        }

        public function isFading():Boolean
        {
            return (_api.isFading());
        }

        public function forceOnGround(_arg_1:Number=200):void
        {
            _api.forceOnGround(_arg_1);
        }

        public function getSizeRatio():Number
        {
            return (_api.getSizeRatio());
        }

        public function setSizeRatio(_arg_1:Number):void
        {
            _api.setSizeRatio(_arg_1);
        }

        public function setVisibility(_arg_1:Boolean):void
        {
            _api.setVisibility(_arg_1);
        }

        public function getPreviousAnimation():String
        {
            return (_api.getPreviousAnimation());
        }

        public function getWeight2():Number
        {
            return (_api.getWeight2());
        }

        public function setWeight2(_arg_1:Number):void
        {
            _api.setWeight2(_arg_1);
        }

        public function getLastHurtAttackBoxStats():Object
        {
            return (_api.getLastHurtAttackBoxStats());
        }

        public function attachHealthBox(_arg_1:String, _arg_2:String, _arg_3:String, _arg_4:int=-1, _arg_5:String=null, _arg_6:int=-1):void
        {
            _api.attachHealthBox(_arg_1, _arg_2, _arg_3, _arg_4, _arg_5, _arg_6);
        }

        public function detachHealthBox():void
        {
            _api.detachHealthBox();
        }

        public function setColorFilters(_arg_1:Object):void
        {
            _api.setColorFilters(_arg_1);
        }

        public function applyPalette(_arg_1:MovieClip):void
        {
            _api.applyPalette(_arg_1);
        }

        public function throbDamageCounter():void
        {
            _api.throbDamageCounter();
        }

        public function getInvincibility():Boolean
        {
            return (_api.getInvincibility());
        }

        public function getIntangibility():Boolean
        {
            return (_api.getIntangibility());
        }

        public function setIntangibility(_arg_1:Boolean):void
        {
            _api.setIntangibility(_arg_1);
        }

        public function setInvincibility(_arg_1:Boolean):void
        {
            _api.setInvincibility(_arg_1);
        }

        public function getClosestLedge():MovieClip
        {
            return (_api.getClosestLedge());
        }

        public function getHealthBox():MovieClip
        {
            return (_api.getHealthBox());
        }

        public function forceAttack(_arg_1:String, _arg_2:*=null, _arg_3:Boolean=false):Boolean
        {
            return (_api.forceAttack(_arg_1, _arg_2, _arg_3));
        }

        public function getPaletteSwapData():Object
        {
            return (_api.getPaletteSwapData());
        }

        public function setPaletteSwapData(_arg_1:Object):void
        {
            _api.setPaletteSwapData(_arg_1);
        }


    }
}//package 

