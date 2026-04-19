package
{
   import flash.display.MovieClip;
   import flash.geom.Point;
   import flash.geom.Rectangle;
   
   public class SSF2GameObject extends SSF2BaseAPIObject
   {
      public function SSF2GameObject(param1:*)
      {
         super(param1);
      }
      
      override public function getType() : String
      {
         return "SSF2GameObject";
      }
      
      public function getOwnStats() : Object
      {
         return {};
      }
      
      public function getAttackStats() : Object
      {
         return {};
      }
      
      public function getProjectileStats() : Object
      {
         return {};
      }
      
      public function getItemStats() : Object
      {
         return {};
      }
      
      public function getGameObjectStat(param1:String) : *
      {
         return _api.getGameObjectStat(param1);
      }
      
      public function playSound(param1:*, param2:Boolean = false) : int
      {
         return _api.playSound(param1,param2);
      }
      
      public function stopSound(param1:int) : void
      {
         _api.stopSound(param1);
      }
      
      public function addToCamera() : void
      {
         _api.addToCamera();
      }
      
      public function addEventListener(param1:String, param2:Function, param3:Object = null) : void
      {
         if(param1 === "projCollideOwner")
         {
            SSF2API.print("Warning!! SSF2Event.PROJ_COLLIDE_OWNER event is deprecated, please use PROJ_COLLIDE event instead");
         }
         _api.addEventListener(param1,param2,param3);
      }
      
      public function hasEventListener(param1:String, param2:Function = null) : Boolean
      {
         return _api.hasEventListener(param1,param2);
      }
      
      public function removeEventListener(param1:String, param2:Function) : void
      {
         _api.removeEventListener(param1,param2);
      }
      
      public function attachEffect(param1:*, param2:Object = null) : MovieClip
      {
         return _api.attachEffect(param1,param2);
      }
      
      public function attachEffectOverlay(param1:*, param2:Object = null) : MovieClip
      {
         return _api.attachEffectOverlay(param1,param2);
      }
      
      public function camFocus(param1:int) : void
      {
         _api.camFocus(param1);
      }
      
      public function camUnfocus() : void
      {
         _api.camUnfocus();
      }
      
      public function createTimer(param1:int, param2:int, param3:Function, param4:Object = null) : void
      {
         _api.createTimer(param1,param2,param3,param4);
      }
      
      public function destroyTimer(param1:Function) : void
      {
         _api.destroyTimer(param1);
      }
      
      public function faceLeft() : void
      {
         _api.faceLeft();
      }
      
      public function faceRight() : void
      {
         _api.faceRight();
      }
      
      public function flip(param1:* = null) : void
      {
         _api.flip(param1);
      }
      
      public function forceHitStun(param1:int, param2:Number = -1) : void
      {
         _api.forceHitStun(param1,param2);
      }
      
      public function getAttackBoxStat(param1:int, param2:String) : *
      {
         return _api.getAttackBoxStat(param1,param2);
      }
      
      public function exportAttackBoxStats(param1:int, param2:String) : Object
      {
         return _api.exportAttackBoxStats(param1,param2);
      }
      
      public function getAttackStat(param1:String) : *
      {
         return _api.getAttackStat(param1);
      }
      
      public function getCounterAttackBoxStats() : Object
      {
         return _api.getCounterAttackBoxStats();
      }
      
      public function getGlobalVariable(param1:String) : *
      {
         return _api.getGlobalVariable(param1);
      }
      
      public function getHeight() : Number
      {
         return _api.getHeight();
      }
      
      public function getHitBox(param1:String) : Object
      {
         return _api.getHitBox(param1);
      }
      
      public function getHomingTarget() : *
      {
         return _api.getHomingTarget();
      }
      
      public function getID() : int
      {
         return _api.getID();
      }
      
      public function getTeamID() : int
      {
         return _api.getTeamID();
      }
      
      public function setTeamID(param1:int) : void
      {
         _api.setTeamID(param1);
      }
      
      public function getLinkageID() : String
      {
         return _api.getLinkageID();
      }
      
      public function getMC() : MovieClip
      {
         return _api.getMC();
      }
      
      public function getProjectiles() : Array
      {
         return _api.getProjectiles();
      }
      
      public function getRotation() : Number
      {
         return _api.getRotation();
      }
      
      public function getScale() : Point
      {
         return _api.getScale();
      }
      
      public function getStanceMC() : MovieClip
      {
         return _api.getStanceMC();
      }
      
      public function getUID() : int
      {
         return _api.getUID();
      }
      
      public function getWidth() : Number
      {
         return _api.getWidth();
      }
      
      public function getX() : Number
      {
         return _api.getX();
      }
      
      public function getXScale() : Number
      {
         return _api.getXScale();
      }
      
      public function getXSpeed() : Number
      {
         return _api.getXSpeed();
      }
      
      public function getY() : Number
      {
         return _api.getY();
      }
      
      public function getYScale() : Number
      {
         return _api.getYScale();
      }
      
      public function getYSpeed() : Number
      {
         return _api.getYSpeed();
      }
      
      public function getNearest(param1:String, param2:Boolean = true, param3:Boolean = true) : *
      {
         return _api.getNearest(param1,param2,param3);
      }
      
      public function getNearestPath(param1:String, param2:Boolean = true, param3:Boolean = true) : Array
      {
         return _api.getNearestPath(param1,param2,param3);
      }
      
      public function getNearestLedge() : MovieClip
      {
         return _api.getNearestLedge();
      }
      
      public function getCurrentPlatform() : *
      {
         return _api.getCurrentPlatform();
      }
      
      public function homeTowardsTarget(param1:Number, param2:*) : void
      {
         _api.homeTowardsTarget(param1,param2);
      }
      
      public function isFacingRight() : Boolean
      {
         return _api.isFacingRight();
      }
      
      public function isOnGround() : Boolean
      {
         return _api.isOnGround();
      }
      
      public function netSpeed(param1:Boolean = false, param2:Boolean = false) : Number
      {
         return _api.netSpeed(param1,param2);
      }
      
      public function netXSpeed(param1:Boolean = false, param2:Boolean = false) : Number
      {
         return _api.netXSpeed(param1,param2);
      }
      
      public function netYSpeed(param1:Boolean = false, param2:Boolean = false) : Number
      {
         return _api.netYSpeed(param1,param2);
      }
      
      public function removeFromCamera() : void
      {
         _api.removeFromCamera();
      }
      
      public function refreshAttackID() : void
      {
         _api.refreshAttackID();
      }
      
      public function refreshStaleID() : void
      {
         _api.refreshStaleID();
      }
      
      public function resetRotation() : void
      {
         _api.resetRotation();
      }
      
      public function resetKnockback() : void
      {
         _api.resetKnockback();
      }
      
      public function resetKnockbackDecay() : void
      {
         _api.resetKnockbackDecay();
      }
      
      public function getKnockbackDecay() : Object
      {
         return _api.getKnockbackDecay();
      }
      
      public function setKnockbackDecay(param1:Number, param2:Number) : void
      {
         _api.setKnockbackDecay(param1,param2);
      }
      
      public function safeMove(param1:Number, param2:Number) : Boolean
      {
         return _api.safeMove(param1,param2);
      }
      
      public function setCamBoxSize(param1:Number, param2:Number, param3:Number = 0, param4:Number = 0) : void
      {
         _api.setCamBoxSize(param1,param2,param3,param4);
      }
      
      public function setGlobalVariable(param1:String, param2:*) : void
      {
         _api.setGlobalVariable(param1,param2);
      }
      
      public function setPosition(param1:Number, param2:Number) : void
      {
         _api.setPosition(param1,param2);
      }
      
      public function setRotation(param1:Number) : void
      {
         _api.setRotation(param1);
      }
      
      public function setScale(param1:Number, param2:Number) : void
      {
         _api.setScale(param1,param2);
      }
      
      public function setX(param1:Number) : void
      {
         _api.setX(param1);
      }
      
      public function setXSpeed(param1:Number, param2:Boolean = true) : void
      {
         _api.setXSpeed(param1,param2);
      }
      
      public function setY(param1:Number) : void
      {
         _api.setY(param1);
      }
      
      public function setYSpeed(param1:Number) : void
      {
         _api.setYSpeed(param1);
      }
      
      public function stancePlayFrame(param1:*) : void
      {
         _api.stancePlayFrame(param1);
      }
      
      public function swapDepths(param1:*) : void
      {
         _api.swapDepths(param1);
      }
      
      public function bringBehind(param1:*) : void
      {
         _api.bringBehind(param1);
      }
      
      public function bringInFront(param1:*) : void
      {
         _api.bringInFront(param1);
      }
      
      public function attachToGround() : void
      {
         _api.attachToGround();
      }
      
      public function unnattachFromGround() : void
      {
         _api.unnattachFromGround();
      }
      
      public function updateAttackBoxStats(param1:int, param2:Object) : void
      {
         _api.updateAttackBoxStats(param1,param2);
      }
      
      public function updateAttackStats(param1:Object) : void
      {
         _api.updateAttackStats(param1);
      }
      
      public function replaceAttackStats(param1:String, param2:Object) : void
      {
         _api.replaceAttackStats(param1,param2);
      }
      
      public function replaceAttackBoxStats(param1:String, param2:int, param3:Object) : void
      {
         _api.replaceAttackBoxStats(param1,param2,param3);
      }
      
      public function inState(param1:uint) : Boolean
      {
         return _api.inState(param1);
      }
      
      public function getState() : uint
      {
         return _api.getState();
      }
      
      public function setState(param1:uint) : void
      {
         _api.setState(param1);
      }
      
      public function extraHitTests(param1:Number, param2:Number, param3:*) : Boolean
      {
         return false;
      }
      
      public function takeDamage(param1:Object, param2:*, param3:Rectangle = null) : Boolean
      {
         return _api.takeDamage(param1,param2,param3);
      }
      
      public function getBoundsRect() : Rectangle
      {
         return _api.getBoundsRect();
      }
      
      public function getCurrentAnimation() : String
      {
         return _api.getCurrentAnimation();
      }
      
      public function getStageParentPosition() : Point
      {
         return _api.getStageParentPosition();
      }
      
      public function applyKnockback(param1:Number, param2:Number) : void
      {
         _api.applyKnockback(param1,param2);
      }
      
      public function applyKnockbackSpeed(param1:Number, param2:Number) : void
      {
         _api.applyKnockbackSpeed(param1,param2);
      }
      
      public function resetFade(param1:int = 15) : void
      {
         _api.resetFade(param1);
      }
      
      public function fadeIn() : void
      {
         _api.fadeIn();
      }
      
      public function fadeOut() : void
      {
         _api.fadeOut();
      }
      
      public function inHitStun() : Boolean
      {
         return _api.inHitStun();
      }
      
      public function inParalysis() : Boolean
      {
         return _api.inParalysis();
      }
      
      public function inLowerLeftWarningBounds() : Boolean
      {
         return _api.inLowerLeftWarningBounds();
      }
      
      public function inUpperLeftWarningBounds() : Boolean
      {
         return _api.inUpperLeftWarningBounds();
      }
      
      public function inLowerRightWarningBounds() : Boolean
      {
         return _api.inLowerRightWarningBounds();
      }
      
      public function inUpperRightWarningBounds() : Boolean
      {
         return _api.inUpperRightWarningBounds();
      }
      
      public function setTargetInterrupt(param1:Function) : void
      {
         _api.setTargetInterrupt(param1);
      }
      
      public function createSelfPlatform(param1:Number, param2:Number, param3:Number, param4:Number, param5:Boolean = true) : *
      {
         return _api.createSelfPlatform(param1,param2,param3,param4,param5,SSF2Platform);
      }
      
      public function createSelfPlatformWithMC(param1:MovieClip, param2:Boolean = true) : *
      {
         return _api.createSelfPlatformWithMC(param1,param2,SSF2Platform);
      }
      
      public function removeSelfPlatform() : void
      {
         _api.removeSelfPlatform();
      }
      
      public function getDamage() : Number
      {
         return _api.getDamage();
      }
      
      public function setDamage(param1:Number) : void
      {
         _api.setDamage(param1);
      }
      
      public function dealDamage(param1:Number) : void
      {
         _api.dealDamage(param1);
      }
      
      public function healDamage(param1:Number) : void
      {
         _api.healDamage(param1);
      }
      
      public function isFading() : Boolean
      {
         return _api.isFading();
      }
      
      public function forceOnGround(param1:Number = 200) : void
      {
         _api.forceOnGround(param1);
      }
      
      public function getSizeRatio() : Number
      {
         return _api.getSizeRatio();
      }
      
      public function setSizeRatio(param1:Number) : void
      {
         _api.setSizeRatio(param1);
      }
      
      public function setVisibility(param1:Boolean) : void
      {
         _api.setVisibility(param1);
      }
      
      public function getPreviousAnimation() : String
      {
         return _api.getPreviousAnimation();
      }
      
      public function getWeight2() : Number
      {
         return _api.getWeight2();
      }
      
      public function setWeight2(param1:Number) : void
      {
         _api.setWeight2(param1);
      }
      
      public function getLastHurtAttackBoxStats() : Object
      {
         return _api.getLastHurtAttackBoxStats();
      }
      
      public function attachHealthBox(param1:String, param2:String, param3:String, param4:int = -1, param5:String = null, param6:int = -1) : void
      {
         _api.attachHealthBox(param1,param2,param3,param4,param5,param6);
      }
      
      public function detachHealthBox() : void
      {
         _api.detachHealthBox();
      }
      
      public function setColorFilters(param1:Object) : void
      {
         _api.setColorFilters(param1);
      }
      
      public function applyPalette(param1:MovieClip) : void
      {
         _api.applyPalette(param1);
      }
      
      public function throbDamageCounter() : void
      {
         _api.throbDamageCounter();
      }
      
      public function getInvincibility() : Boolean
      {
         return _api.getInvincibility();
      }
      
      public function getIntangibility() : Boolean
      {
         return _api.getIntangibility();
      }
      
      public function setIntangibility(param1:Boolean) : void
      {
         _api.setIntangibility(param1);
      }
      
      public function setInvincibility(param1:Boolean) : void
      {
         _api.setInvincibility(param1);
      }
      
      public function getClosestLedge() : MovieClip
      {
         return _api.getClosestLedge();
      }
      
      public function getHealthBox() : MovieClip
      {
         return _api.getHealthBox();
      }
      
      public function forceAttack(param1:String, param2:* = null, param3:Boolean = false) : Boolean
      {
         return _api.forceAttack(param1,param2,param3);
      }
      
      public function getPaletteSwapData() : Object
      {
         return _api.getPaletteSwapData();
      }
      
      public function setPaletteSwapData(param1:Object) : void
      {
         _api.setPaletteSwapData(param1);
      }
   }
}

