// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//SSF2Character

package 
{
    import flash.geom.Point;
    import flash.display.MovieClip;

    public class SSF2Character extends SSF2GameObject 
    {

        public function SSF2Character(_arg_1:*):void
        {
            super(_arg_1);
        }

        override public function getType():String
        {
            return ("SSF2Character");
        }

        public function get KirbyPower():String
        {
            return (_api.KirbyPower);
        }

        public function set KirbyPower(_arg_1:String):void
        {
            _api.KirbyPower = _arg_1;
        }

        override public function inState(_arg_1:uint):Boolean
        {
            if (isDisposed())
            {
                SSF2API.print((("Warning: API attempted to check inState(CState." + CState.toString(_arg_1)) + ") after object has been disposed!"));
                return (_arg_1 === 42);
            };
            return (super.inState(_arg_1));
        }

        override public function setState(_arg_1:uint):void
        {
            if ((_arg_1 === 42))
            {
                SSF2API.print("Warning: Cannot explicitly set SSF2Character to DEAD state. Please use destroy() method instead.");
            };
            super.setState(_arg_1);
        }

        public function shootOutOpponent():void
        {
            _api.shootOutOpponent();
        }

        public function activateFinalForm():void
        {
            _api.activateFinalForm();
        }

        public function dropItem(_arg_1:Boolean=false):void
        {
            _api.dropItem(_arg_1);
        }

        public function endAttack(_arg_1:String=null, _arg_2:String=null):void
        {
            _api.endAttack(_arg_1, _arg_2);
        }

        public function endFinalForm():void
        {
            _api.endFinalForm();
        }

        public function fireProjectile(_arg_1:*, _arg_2:Number=0, _arg_3:Number=0, _arg_4:Boolean=false, _arg_5:Object=null):*
        {
            return (_api.fireProjectile(_arg_1, _arg_2, _arg_3, _arg_4, _arg_5));
        }

        public function rocketCharacter(_arg_1:Number, _arg_2:Number, _arg_3:Number, _arg_4:Boolean):void
        {
            _api.rocketCharacter(_arg_1, _arg_2, _arg_3, _arg_4);
        }

        public function forceGrabbedHurtFrame(_arg_1:String):void
        {
            _api.forceGrabbedHurtFrame(_arg_1);
        }

        public function generateItem(_arg_1:String, _arg_2:Boolean=false, _arg_3:Boolean=true, _arg_4:Boolean=false):*
        {
            return (_api.generateItem(_arg_1, _arg_2, _arg_3, _arg_4));
        }

        public function generateCharacterItem(_arg_1:String, _arg_2:String, _arg_3:Boolean=false):*
        {
            return (_api.generateCharacterItem(_arg_1, _arg_2, _arg_3));
        }

        public function getCharacterStat(_arg_1:String):*
        {
            return (_api.getCharacterStat(_arg_1));
        }

        public function getPlayerSetting(_arg_1:String):*
        {
            return (_api.getPlayerSetting(_arg_1));
        }

        public function getControls(_arg_1:Boolean=false):Object
        {
            return (_api.getControls(_arg_1));
        }

        public function getControlBits(_arg_1:Boolean=false):ControlBits
        {
            return (new ControlBits(_api.getControlBits(_arg_1)));
        }

        public function getCostume():int
        {
            return (_api.getCostume());
        }

        public function setCostume(_arg_1:int, _arg_2:int=-1):void
        {
            _api.setCostume(_arg_1, _arg_2);
        }

        public function getCPUAction():int
        {
            return (_api.getCPUAction());
        }

        public function getCPUForcedAction():int
        {
            return (_api.getCPUForcedAction());
        }

        public function setCPUForcedAction(_arg_1:int):void
        {
            _api.setCPUForcedAction(_arg_1);
        }

        public function getCPULevel():int
        {
            return (_api.getCPULevel());
        }

        public function getCPUTarget():*
        {
            return (_api.getCPUTarget());
        }

        public function getCurrentAttackFrame():String
        {
            return (_api.getCurrentAttackFrame());
        }

        public function getCurrentKirbyPower():String
        {
            return (_api.getCurrentKirbyPower());
        }

        public function getCurrentProjectile():*
        {
            return (_api.getCurrentProjectile());
        }

        public function getExecTime():int
        {
            return (_api.getExecTime());
        }

        public function getHitsDealtCounter():int
        {
            return (_api.getHitsDealtCounter());
        }

        public function getHitsReceivedCounter():int
        {
            return (_api.getHitsReceivedCounter());
        }

        public function getGrabbedOpponent():*
        {
            SSF2API.print("Warning: getGrabbedOpponent() is deprecated. Please replace with getGrabbedOpponents():Array");
            return (_api.getGrabbedOpponent());
        }

        public function getGrabbedOpponents():Array
        {
            return (_api.getGrabbedOpponents());
        }

        public function getGrabber():*
        {
            return (_api.getGrabber());
        }

        public function getItem():*
        {
            return (_api.getItem());
        }

        public function getLastUsed(_arg_1:String=null):int
        {
            SSF2API.print("Warning: getLastUsed() is deprecated. Please replace with custom implementation instead.");
            return (_api.getLastUsed(_arg_1));
        }

        public function getLives():int
        {
            return (_api.getLives());
        }

        public function getShieldPower():Number
        {
            return (_api.getShieldPower());
        }

        public function getSizeStatus():int
        {
            return (_api.getSizeStatus());
        }

        public function getSmashTimer():int
        {
            return (_api.getSmashTimer());
        }

        public function getTeammates():Array
        {
            return (_api.getTeammates());
        }

        public function getTetherCount():int
        {
            return (_api.getTetherCount());
        }

        public function gotoGrabbedCharacter():void
        {
            _api.gotoGrabbedCharacter();
        }

        public function grabRelease():void
        {
            _api.grabRelease();
        }

        public function grabReleaseOpponent():void
        {
            _api.grabReleaseOpponent();
        }

        public function importCPUControls(_arg_1:Array):void
        {
            _api.importCPUControls(_arg_1);
        }

        public function initiateCrash():void
        {
            _api.initiateCrash();
        }

        public function isCPU():Boolean
        {
            return (_api.isCPU());
        }

        public function isForcedCrash():Boolean
        {
            return (_api.isForcedCrash());
        }

        public function isGrabbing():Boolean
        {
            return (_api.isGrabbing());
        }

        public function isRecovering():Boolean
        {
            return (_api.isRecovering());
        }

        public function isCPURecovering():Boolean
        {
            return (_api.isCPURecovering());
        }

        public function isStandby():Boolean
        {
            return (_api.isStandby());
        }

        public function confuseAI(_arg_1:int):void
        {
            _api.confuseAI(_arg_1);
        }

        public function jumpFullyReleased():Boolean
        {
            return (_api.jumpFullyReleased());
        }

        public function maxOutJumps():void
        {
            _api.maxOutJumps();
        }

        public function playCharacterSound(_arg_1:String):int
        {
            return (_api.playCharacterSound(_arg_1));
        }

        public function playAttackSound(_arg_1:Number=-1):int
        {
            return (_api.playAttackSound(_arg_1));
        }

        public function playVoiceSound(_arg_1:Number=-1):int
        {
            return (_api.playVoiceSound(_arg_1));
        }

        public function recover(_arg_1:int):Boolean
        {
            return (_api.recover(_arg_1));
        }

        public function releaseLedge():void
        {
            _api.releaseLedge();
        }

        public function releaseOpponent():void
        {
            _api.releaseOpponent();
        }

        public function removeItem():void
        {
            _api.removeItem();
        }

        public function replaceCharacter(_arg_1:String, _arg_2:String=null, _arg_3:String=null):void
        {
            _api.replaceCharacter(_arg_1, _arg_2, _arg_3);
        }

        public function resetCPUControls():void
        {
            _api.resetCPUControls();
        }

        public function resetHitsDealtCounter():void
        {
            _api.resetHitsDealtCounter();
        }

        public function resetHitsReceivedCounter():void
        {
            _api.resetHitsReceivedCounter();
        }

        public function resetJumps():void
        {
            _api.resetJumps();
        }

        public function resetMovement(_arg_1:*=null):void
        {
            _api.resetMovement(_arg_1);
        }

        public function resetStaleMoves():void
        {
            _api.resetStaleMoves();
        }

        public function setAttackEnabled(_arg_1:Boolean, _arg_2:String=null, _arg_3:int=-1):void
        {
            _api.setAttackEnabled(_arg_1, _arg_2, _arg_3);
        }

        public function setCPUAttackQueue(_arg_1:String):void
        {
            _api.setCPUAttackQueue(_arg_1);
        }

        public function setInvisibilityTimer(_arg_1:int):void
        {
            _api.setInvisibilityTimer(_arg_1);
        }

        public function setLastUsed(_arg_1:String, _arg_2:int):void
        {
            _api.setLastUsed(_arg_1, _arg_2);
        }

        public function setSizeStatus(_arg_1:int):void
        {
            _api.setSizeStatus(_arg_1);
        }

        public function swapDepthsWithGrabbedOpponent(_arg_1:Boolean):void
        {
            _api.swapDepthsWithGrabbedOpponent(_arg_1);
        }

        public function switchAttack(_arg_1:String, _arg_2:*=null):void
        {
            _api.switchAttack(_arg_1, _arg_2);
        }

        public function switchAttackData(_arg_1:String, _arg_2:String):void
        {
            _api.switchAttackData(_arg_1, _arg_2);
        }

        public function toBounce(_arg_1:*=null):void
        {
            _api.toBounce(_arg_1);
        }

        public function toCrashLand(_arg_1:*=null):void
        {
            _api.toCrashLand(_arg_1);
        }

        public function toHeavyLand(_arg_1:*=null):void
        {
            _api.toHeavyLand(_arg_1);
        }

        public function toHelpless(_arg_1:*=null):void
        {
            _api.toHelpless(_arg_1);
        }

        public function toIdle(_arg_1:*=null):void
        {
            _api.toIdle(_arg_1);
        }

        public function toLand(_arg_1:*=null):void
        {
            _api.toLand(_arg_1);
        }

        public function toToss(_arg_1:*=null):void
        {
            _api.toToss(_arg_1);
        }

        public function toFlying(_arg_1:*=null):void
        {
            _api.toFlying(_arg_1);
        }

        public function toBarrel(_arg_1:*=null):void
        {
            _api.toBarrel(_arg_1);
        }

        public function toGrabbing(_arg_1:*=null):void
        {
            _api.toGrabbing(_arg_1);
        }

        public function toRoll(_arg_1:*=null):void
        {
            _api.toRoll(_arg_1);
        }

        public function toDodgeRoll(_arg_1:*=null):void
        {
            _api.toDodgeRoll(_arg_1);
        }

        public function toJumpChamber(_arg_1:*=null):void
        {
            _api.toJumpChamber();
        }

        public function toJump(_arg_1:*=null):void
        {
            _api.toJump();
        }

        public function toDoubleJump(_arg_1:*=null):void
        {
            _api.toDoubleJump();
        }

        public function tossItem(_arg_1:Number):void
        {
            _api.tossItem(_arg_1);
        }

        public function pickupItem():Boolean
        {
            return (_api.pickupItem());
        }

        public function updateCharacterStats(_arg_1:Object):void
        {
            _api.updateCharacterStats(_arg_1);
        }

        public function updatePlayerSettings(_arg_1:Object):void
        {
            _api.updatePlayerSettings(_arg_1);
        }

        public function usingCPUControls():Boolean
        {
            return (_api.usingCPUControls());
        }

        public function getRank():int
        {
            return (_api.getRank());
        }

        public function setRank(_arg_1:int):void
        {
            _api.setRank(_arg_1);
        }

        public function getForceTransformTime():int
        {
            return (_api.getForceTransformTime());
        }

        public function setStarmanInvincibility(_arg_1:int):void
        {
            _api.setStarmanInvincibility(_arg_1);
        }

        public function setHurtInterrupt(_arg_1:Function):void
        {
            _api.setHurtInterrupt(_arg_1);
        }

        public function forceTaunt():void
        {
            _api.forceTaunt();
        }

        public function warioWareEffect(_arg_1:Boolean, _arg_2:Boolean):void
        {
            _api.warioWareEffect(_arg_1, _arg_2);
        }

        public function isUsingFinalSmash():Boolean
        {
            return (_api.isUsingFinalSmash());
        }

        public function grab(_arg_1:int=-1, _arg_2:Boolean=true, _arg_3:Boolean=false, _arg_4:Boolean=false):Boolean
        {
            return (_api.grab(_arg_1, _arg_2, _arg_3, _arg_4));
        }

        public function release():void
        {
            _api.release();
        }

        public function triggerFSCutscene():void
        {
            _api.triggerFSCutscene();
        }

        public function killFSCutscene():void
        {
            _api.killFSCutscene();
        }

        public function getOriginalSizeRatio():Number
        {
            return (_api.getOriginalSizeRatio());
        }

        public function setOriginalSizeRatio(_arg_1:Number):void
        {
            _api.setOriginalSizeRatio(_arg_1);
        }

        public function lockSizeStatus(_arg_1:Boolean):void
        {
            _api.lockSizeStatus(_arg_1);
        }

        public function getStartPosition():Point
        {
            return (_api.getStartPosition());
        }

        public function setStartPosition(_arg_1:Point):void
        {
            _api.setStartPosition(_arg_1);
        }

        public function getSpawnPosition():Point
        {
            return (_api.getSpawnPosition());
        }

        public function setSpawnPosition(_arg_1:Point):void
        {
            _api.setSpawnPosition(_arg_1);
        }

        public function setOffScreenIndicatorEnabled(_arg_1:Boolean):void
        {
            _api.setOffScreenIndicatorEnabled(_arg_1);
        }

        public function setHumanControl(_arg_1:Boolean, _arg_2:Number=1):void
        {
            _api.setHumanControl(_arg_1, _arg_2);
        }

        public function getStandby():Boolean
        {
            return (_api.getStandby());
        }

        public function setStandby(_arg_1:Boolean):void
        {
            _api.setStandby(_arg_1);
        }

        public function getHitLag():int
        {
            return (_api.getHitLag());
        }

        public function setHitLag(_arg_1:int):void
        {
            _api.setHitLag(_arg_1);
        }

        public function grantFinalSmash(_arg_1:*=null):Boolean
        {
            return (_api.grantFinalSmash(_arg_1));
        }

        public function releaseSmashBall():Boolean
        {
            return (_api.releaseSmashBall());
        }

        public function setLivesEnabled(_arg_1:Boolean):void
        {
            _api.setLivesEnabled(_arg_1);
        }

        public function setLives(_arg_1:int):void
        {
            _api.setLives(_arg_1);
        }

        public function setMetalStatus(_arg_1:Boolean):void
        {
            _api.setMetalStatus(_arg_1);
        }

        public function getMetalStatus():Boolean
        {
            return (_api.getMetalStatus());
        }

        public function getPoison():Object
        {
            return (_api.getPoison());
        }

        public function setPoison(_arg_1:int, _arg_2:int=15, _arg_3:int=300):void
        {
            _api.setPoison(_arg_1, _arg_2, _arg_3);
        }

        public function hasSmashBallAura():Boolean
        {
            return (_api.hasSmashBallAura());
        }

        public function getFinalSmashCutscene():MovieClip
        {
            return (_api.getFinalSmashCutscene());
        }

        public function getFinalSmashReticule():MovieClip
        {
            return (_api.getFinalSmashReticule());
        }

        public function destroy():MovieClip
        {
            return (_api.destroy());
        }

        public function getMatchStatistics():Object
        {
            return (_api.getMatchStatistics());
        }

        public function getKirbyHatMC():MovieClip
        {
            return (_api.getKirbyHatMC());
        }

        public function getMidairJumpCount():int
        {
            return (_api.getMidairJumpCount());
        }

        public function setMidairJumpCount(_arg_1:int):void
        {
            _api.setMidairJumpCount(_arg_1);
        }

        public function setIASA(_arg_1:Boolean):void
        {
            _api.setIASA(_arg_1);
        }

        public function getFinalSmashMeterCharge():Number
        {
            return (_api.getFinalSmashMeterCharge());
        }

        public function setFinalSmashMeterCharge(_arg_1:Number):void
        {
            _api.setFinalSmashMeterCharge(_arg_1);
        }


    }
}//package 

