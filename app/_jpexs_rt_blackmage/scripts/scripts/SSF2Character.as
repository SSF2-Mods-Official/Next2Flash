package
{
   import flash.display.MovieClip;
   import flash.geom.Point;
   
   public class SSF2Character extends SSF2GameObject
   {
      public function SSF2Character(param1:*)
      {
         super(param1);
      }
      
      override public function getType() : String
      {
         return "SSF2Character";
      }
      
      public function get KirbyPower() : String
      {
         return _api.KirbyPower;
      }
      
      public function set KirbyPower(param1:String) : void
      {
         _api.KirbyPower = param1;
      }
      
      override public function inState(param1:uint) : Boolean
      {
         if(isDisposed())
         {
            SSF2API.print("Warning: API attempted to check inState(CState." + CState.toString(param1) + ") after object has been disposed!");
            return param1 === 42;
         }
         return super.inState(param1);
      }
      
      override public function setState(param1:uint) : void
      {
         if(param1 === 42)
         {
            SSF2API.print("Warning: Cannot explicitly set SSF2Character to DEAD state. Please use destroy() method instead.");
         }
         super.setState(param1);
      }
      
      public function shootOutOpponent() : void
      {
         _api.shootOutOpponent();
      }
      
      public function activateFinalForm() : void
      {
         _api.activateFinalForm();
      }
      
      public function dropItem(param1:Boolean = false) : void
      {
         _api.dropItem(param1);
      }
      
      public function endAttack(param1:String = null, param2:String = null) : void
      {
         _api.endAttack(param1,param2);
      }
      
      public function endFinalForm() : void
      {
         _api.endFinalForm();
      }
      
      public function fireProjectile(param1:*, param2:Number = 0, param3:Number = 0, param4:Boolean = false, param5:Object = null) : *
      {
         return _api.fireProjectile(param1,param2,param3,param4,param5);
      }
      
      public function rocketCharacter(param1:Number, param2:Number, param3:Number, param4:Boolean) : void
      {
         _api.rocketCharacter(param1,param2,param3,param4);
      }
      
      public function forceGrabbedHurtFrame(param1:String) : void
      {
         _api.forceGrabbedHurtFrame(param1);
      }
      
      public function generateItem(param1:String, param2:Boolean = false, param3:Boolean = true, param4:Boolean = false) : *
      {
         return _api.generateItem(param1,param2,param3,param4);
      }
      
      public function generateCharacterItem(param1:String, param2:String, param3:Boolean = false) : *
      {
         return _api.generateCharacterItem(param1,param2,param3);
      }
      
      public function getCharacterStat(param1:String) : *
      {
         return _api.getCharacterStat(param1);
      }
      
      public function getPlayerSetting(param1:String) : *
      {
         return _api.getPlayerSetting(param1);
      }
      
      public function getControls(param1:Boolean = false) : Object
      {
         return _api.getControls(param1);
      }
      
      public function getControlBits(param1:Boolean = false) : ControlBits
      {
         return new ControlBits(_api.getControlBits(param1));
      }
      
      public function getCostume() : int
      {
         return _api.getCostume();
      }
      
      public function setCostume(param1:int, param2:int = -1) : void
      {
         _api.setCostume(param1,param2);
      }
      
      public function getCPUAction() : int
      {
         return _api.getCPUAction();
      }
      
      public function getCPUForcedAction() : int
      {
         return _api.getCPUForcedAction();
      }
      
      public function setCPUForcedAction(param1:int) : void
      {
         _api.setCPUForcedAction(param1);
      }
      
      public function getCPULevel() : int
      {
         return _api.getCPULevel();
      }
      
      public function getCPUTarget() : *
      {
         return _api.getCPUTarget();
      }
      
      public function getCurrentAttackFrame() : String
      {
         return _api.getCurrentAttackFrame();
      }
      
      public function getCurrentKirbyPower() : String
      {
         return _api.getCurrentKirbyPower();
      }
      
      public function getCurrentProjectile() : *
      {
         return _api.getCurrentProjectile();
      }
      
      public function getExecTime() : int
      {
         return _api.getExecTime();
      }
      
      public function getHitsDealtCounter() : int
      {
         return _api.getHitsDealtCounter();
      }
      
      public function getHitsReceivedCounter() : int
      {
         return _api.getHitsReceivedCounter();
      }
      
      public function getGrabbedOpponent() : *
      {
         SSF2API.print("Warning: getGrabbedOpponent() is deprecated. Please replace with getGrabbedOpponents():Array");
         return _api.getGrabbedOpponent();
      }
      
      public function getGrabbedOpponents() : Array
      {
         return _api.getGrabbedOpponents();
      }
      
      public function getGrabber() : *
      {
         return _api.getGrabber();
      }
      
      public function getItem() : *
      {
         return _api.getItem();
      }
      
      public function getLastUsed(param1:String = null) : int
      {
         SSF2API.print("Warning: getLastUsed() is deprecated. Please replace with custom implementation instead.");
         return _api.getLastUsed(param1);
      }
      
      public function getLives() : int
      {
         return _api.getLives();
      }
      
      public function getShieldPower() : Number
      {
         return _api.getShieldPower();
      }
      
      public function getSizeStatus() : int
      {
         return _api.getSizeStatus();
      }
      
      public function getSmashTimer() : int
      {
         return _api.getSmashTimer();
      }
      
      public function getTeammates() : Array
      {
         return _api.getTeammates();
      }
      
      public function getTetherCount() : int
      {
         return _api.getTetherCount();
      }
      
      public function gotoGrabbedCharacter() : void
      {
         _api.gotoGrabbedCharacter();
      }
      
      public function grabRelease() : void
      {
         _api.grabRelease();
      }
      
      public function grabReleaseOpponent() : void
      {
         _api.grabReleaseOpponent();
      }
      
      public function importCPUControls(param1:Array) : void
      {
         _api.importCPUControls(param1);
      }
      
      public function initiateCrash() : void
      {
         _api.initiateCrash();
      }
      
      public function isCPU() : Boolean
      {
         return _api.isCPU();
      }
      
      public function isForcedCrash() : Boolean
      {
         return _api.isForcedCrash();
      }
      
      public function isGrabbing() : Boolean
      {
         return _api.isGrabbing();
      }
      
      public function isRecovering() : Boolean
      {
         return _api.isRecovering();
      }
      
      public function isCPURecovering() : Boolean
      {
         return _api.isCPURecovering();
      }
      
      public function isStandby() : Boolean
      {
         return _api.isStandby();
      }
      
      public function confuseAI(param1:int) : void
      {
         _api.confuseAI(param1);
      }
      
      public function jumpFullyReleased() : Boolean
      {
         return _api.jumpFullyReleased();
      }
      
      public function maxOutJumps() : void
      {
         _api.maxOutJumps();
      }
      
      public function playCharacterSound(param1:String) : int
      {
         return _api.playCharacterSound(param1);
      }
      
      public function playAttackSound(param1:Number = -1) : int
      {
         return _api.playAttackSound(param1);
      }
      
      public function playVoiceSound(param1:Number = -1) : int
      {
         return _api.playVoiceSound(param1);
      }
      
      public function recover(param1:int) : Boolean
      {
         return _api.recover(param1);
      }
      
      public function releaseLedge() : void
      {
         _api.releaseLedge();
      }
      
      public function releaseOpponent() : void
      {
         _api.releaseOpponent();
      }
      
      public function removeItem() : void
      {
         _api.removeItem();
      }
      
      public function replaceCharacter(param1:String, param2:String = null, param3:String = null) : void
      {
         _api.replaceCharacter(param1,param2,param3);
      }
      
      public function resetCPUControls() : void
      {
         _api.resetCPUControls();
      }
      
      public function resetHitsDealtCounter() : void
      {
         _api.resetHitsDealtCounter();
      }
      
      public function resetHitsReceivedCounter() : void
      {
         _api.resetHitsReceivedCounter();
      }
      
      public function resetJumps() : void
      {
         _api.resetJumps();
      }
      
      public function resetMovement(param1:* = null) : void
      {
         _api.resetMovement(param1);
      }
      
      public function resetStaleMoves() : void
      {
         _api.resetStaleMoves();
      }
      
      public function setAttackEnabled(param1:Boolean, param2:String = null, param3:int = -1) : void
      {
         _api.setAttackEnabled(param1,param2,param3);
      }
      
      public function setCPUAttackQueue(param1:String) : void
      {
         _api.setCPUAttackQueue(param1);
      }
      
      public function setInvisibilityTimer(param1:int) : void
      {
         _api.setInvisibilityTimer(param1);
      }
      
      public function setLastUsed(param1:String, param2:int) : void
      {
         _api.setLastUsed(param1,param2);
      }
      
      public function setSizeStatus(param1:int) : void
      {
         _api.setSizeStatus(param1);
      }
      
      public function swapDepthsWithGrabbedOpponent(param1:Boolean) : void
      {
         _api.swapDepthsWithGrabbedOpponent(param1);
      }
      
      public function switchAttack(param1:String, param2:* = null) : void
      {
         _api.switchAttack(param1,param2);
      }
      
      public function switchAttackData(param1:String, param2:String) : void
      {
         _api.switchAttackData(param1,param2);
      }
      
      public function toBounce(param1:* = null) : void
      {
         _api.toBounce(param1);
      }
      
      public function toCrashLand(param1:* = null) : void
      {
         _api.toCrashLand(param1);
      }
      
      public function toHeavyLand(param1:* = null) : void
      {
         _api.toHeavyLand(param1);
      }
      
      public function toHelpless(param1:* = null) : void
      {
         _api.toHelpless(param1);
      }
      
      public function toIdle(param1:* = null) : void
      {
         _api.toIdle(param1);
      }
      
      public function toLand(param1:* = null) : void
      {
         _api.toLand(param1);
      }
      
      public function toToss(param1:* = null) : void
      {
         _api.toToss(param1);
      }
      
      public function toFlying(param1:* = null) : void
      {
         _api.toFlying(param1);
      }
      
      public function toBarrel(param1:* = null) : void
      {
         _api.toBarrel(param1);
      }
      
      public function toGrabbing(param1:* = null) : void
      {
         _api.toGrabbing(param1);
      }
      
      public function toRoll(param1:* = null) : void
      {
         _api.toRoll(param1);
      }
      
      public function toDodgeRoll(param1:* = null) : void
      {
         _api.toDodgeRoll(param1);
      }
      
      public function toJumpChamber(param1:* = null) : void
      {
         _api.toJumpChamber();
      }
      
      public function toJump(param1:* = null) : void
      {
         _api.toJump();
      }
      
      public function toDoubleJump(param1:* = null) : void
      {
         _api.toDoubleJump();
      }
      
      public function tossItem(param1:Number) : void
      {
         _api.tossItem(param1);
      }
      
      public function pickupItem() : Boolean
      {
         return _api.pickupItem();
      }
      
      public function updateCharacterStats(param1:Object) : void
      {
         _api.updateCharacterStats(param1);
      }
      
      public function updatePlayerSettings(param1:Object) : void
      {
         _api.updatePlayerSettings(param1);
      }
      
      public function usingCPUControls() : Boolean
      {
         return _api.usingCPUControls();
      }
      
      public function getRank() : int
      {
         return _api.getRank();
      }
      
      public function setRank(param1:int) : void
      {
         _api.setRank(param1);
      }
      
      public function getForceTransformTime() : int
      {
         return _api.getForceTransformTime();
      }
      
      public function setStarmanInvincibility(param1:int) : void
      {
         _api.setStarmanInvincibility(param1);
      }
      
      public function setHurtInterrupt(param1:Function) : void
      {
         _api.setHurtInterrupt(param1);
      }
      
      public function forceTaunt() : void
      {
         _api.forceTaunt();
      }
      
      public function warioWareEffect(param1:Boolean, param2:Boolean) : void
      {
         _api.warioWareEffect(param1,param2);
      }
      
      public function isUsingFinalSmash() : Boolean
      {
         return _api.isUsingFinalSmash();
      }
      
      public function grab(param1:int = -1, param2:Boolean = true, param3:Boolean = false, param4:Boolean = false) : Boolean
      {
         return _api.grab(param1,param2,param3,param4);
      }
      
      public function release() : void
      {
         _api.release();
      }
      
      public function triggerFSCutscene() : void
      {
         _api.triggerFSCutscene();
      }
      
      public function killFSCutscene() : void
      {
         _api.killFSCutscene();
      }
      
      public function getOriginalSizeRatio() : Number
      {
         return _api.getOriginalSizeRatio();
      }
      
      public function setOriginalSizeRatio(param1:Number) : void
      {
         _api.setOriginalSizeRatio(param1);
      }
      
      public function lockSizeStatus(param1:Boolean) : void
      {
         _api.lockSizeStatus(param1);
      }
      
      public function getStartPosition() : Point
      {
         return _api.getStartPosition();
      }
      
      public function setStartPosition(param1:Point) : void
      {
         _api.setStartPosition(param1);
      }
      
      public function getSpawnPosition() : Point
      {
         return _api.getSpawnPosition();
      }
      
      public function setSpawnPosition(param1:Point) : void
      {
         _api.setSpawnPosition(param1);
      }
      
      public function setOffScreenIndicatorEnabled(param1:Boolean) : void
      {
         _api.setOffScreenIndicatorEnabled(param1);
      }
      
      public function setHumanControl(param1:Boolean, param2:Number = 1) : void
      {
         _api.setHumanControl(param1,param2);
      }
      
      public function getStandby() : Boolean
      {
         return _api.getStandby();
      }
      
      public function setStandby(param1:Boolean) : void
      {
         _api.setStandby(param1);
      }
      
      public function getHitLag() : int
      {
         return _api.getHitLag();
      }
      
      public function setHitLag(param1:int) : void
      {
         _api.setHitLag(param1);
      }
      
      public function grantFinalSmash(param1:* = null) : Boolean
      {
         return _api.grantFinalSmash(param1);
      }
      
      public function releaseSmashBall() : Boolean
      {
         return _api.releaseSmashBall();
      }
      
      public function setLivesEnabled(param1:Boolean) : void
      {
         _api.setLivesEnabled(param1);
      }
      
      public function setLives(param1:int) : void
      {
         _api.setLives(param1);
      }
      
      public function setMetalStatus(param1:Boolean) : void
      {
         _api.setMetalStatus(param1);
      }
      
      public function getMetalStatus() : Boolean
      {
         return _api.getMetalStatus();
      }
      
      public function getPoison() : Object
      {
         return _api.getPoison();
      }
      
      public function setPoison(param1:int, param2:int = 15, param3:int = 300) : void
      {
         _api.setPoison(param1,param2,param3);
      }
      
      public function hasSmashBallAura() : Boolean
      {
         return _api.hasSmashBallAura();
      }
      
      public function getFinalSmashCutscene() : MovieClip
      {
         return _api.getFinalSmashCutscene();
      }
      
      public function getFinalSmashReticule() : MovieClip
      {
         return _api.getFinalSmashReticule();
      }
      
      public function destroy() : MovieClip
      {
         return _api.destroy();
      }
      
      public function getMatchStatistics() : Object
      {
         return _api.getMatchStatistics();
      }
      
      public function getKirbyHatMC() : MovieClip
      {
         return _api.getKirbyHatMC();
      }
      
      public function getMidairJumpCount() : int
      {
         return _api.getMidairJumpCount();
      }
      
      public function setMidairJumpCount(param1:int) : void
      {
         _api.setMidairJumpCount(param1);
      }
      
      public function setIASA(param1:Boolean) : void
      {
         _api.setIASA(param1);
      }
      
      public function getFinalSmashMeterCharge() : Number
      {
         return _api.getFinalSmashMeterCharge();
      }
      
      public function setFinalSmashMeterCharge(param1:Number) : void
      {
         _api.setFinalSmashMeterCharge(param1);
      }
   }
}

