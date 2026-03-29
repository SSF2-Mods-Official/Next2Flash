package captainfalcon_fla
{
    import flash.display.MovieClip;

    public dynamic class NSpecial_60 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var itemBox:MovieClip;
        public var self:CaptainExt;
        public var reverseStats:*;
        public var reversed:Boolean;
        public var curFrame:*;
        public var atkID:*;
        public var atkilled:Boolean;
        public var charge:*;
        public var controls:*;

        public function NSpecial_60()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 2, this.frame3, 4, this.frame5, 23, this.frame24, 24, this.frame25, 25, this.frame26, 26, this.frame27, 28, this.frame29, 35, this.frame36, 50, this.frame51, 51, this.frame52, 55, this.frame56, 60, this.frame61);
        }

        public function checkSpeckill():void
        {
            if (!this.self.inState(CState.ATTACKING))
            {
                this.self.destroyTimer(this.checkSpeckill);
                this.self.setGlobalVariable("FalconPunchReversed", false);
                this.self.setGlobalVariable("FalconPunchAtkID", null);
                this.self.setGlobalVariable("FalconPunchFrame", 0);
                this.stopSFX();
            };
        }

        public function toAir(_arg_1:*):void
        {
            this.self.destroyTimer(this.checkSpeckill);
            this.self.removeEventListener(SSF2Event.GROUND_LEAVE, this.toAir);
            this.self.setGlobalVariable("FalconPunchReversed", this.reversed);
            this.self.setGlobalVariable("FalconPunchAtkID", this.self.getAttackStat("atk_id"));
            this.self.setGlobalVariable("FalconPunchFrame", currentFrame);
            this.self.forceAttack("b_air", null, true);
        }

        public function stopSFX():void
        {
            var _local_1:* = this.self.getGlobalVariable("FalconPunchSFX");
            if (_local_1 != null)
            {
                SSF2API.stopSound(_local_1);
                this.self.setGlobalVariable("FalconPunchSFX", null);
            };
            _local_1 = this.self.getGlobalVariable("FalconPunchVFX");
            if (_local_1 != null)
            {
                SSF2API.stopSound(_local_1);
                this.self.setGlobalVariable("FalconPunchVFX", null);
            };
        }

        public function killAttackboxes():void
        {
            SSF2API.print("ha ha you dorks failed.");
            this.self.updateAttackBoxStats(1, {
                "damage":0,
                "power":0,
                "kbConstant":0,
                "hasEffect":false
            });
            this.self.updateAttackBoxStats(2, {
                "damage":0,
                "power":0,
                "kbConstant":0,
                "hasEffect":false
            });
            this.atkilled = true;
        }

        public function checkAtkilled():void
        {
            if (this.atkilled)
            {
                this.self.updateAttackStats({"atk_id":this.atkID});
                if (this.reversed)
                {
                    this.self.updateAttackBoxStats(1, {
                        "atk_id":this.atkID,
                        "hasEffect":true
                    });
                    this.self.updateAttackBoxStats(2, {
                        "atk_id":this.atkID,
                        "hasEffect":true
                    });
                    this.self.updateAttackBoxStats(1, this.reverseStats);
                    this.self.updateAttackBoxStats(2, this.reverseStats);
                }
                else
                {
                    this.self.updateAttackBoxStats(1, {
                        "atk_id":this.atkID,
                        "damage":25,
                        "power":45,
                        "kbConstant":100,
                        "hasEffect":true
                    });
                    this.self.updateAttackBoxStats(2, {
                        "atk_id":this.atkID,
                        "damage":25,
                        "power":45,
                        "kbConstant":100,
                        "hasEffect":true
                    });
                };
                this.atkilled = false;
            };
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as CaptainExt);
            this.reverseStats = {
                "damage":28,
                "direction":35,
                "power":50,
                "kbConstant":100,
                "hitStun":11,
                "selfHitStun":9
            };
            if (SSF2API.isReady() && this.self)
            {
                this.reversed = this.self.getGlobalVariable("FalconPunchReversed");
                this.curFrame = this.self.getGlobalVariable("FalconPunchFrame");
                this.atkID = this.self.getGlobalVariable("FalconPunchAtkID");
                this.atkilled = false;
                this.self.createTimer(1, -1, this.checkSpeckill, {"persistent":true});
                this.self.addEventListener(SSF2Event.GROUND_LEAVE, this.toAir);
                if (this.reversed)
                {
                    this.self.updateAttackBoxStats(1, this.reverseStats);
                    this.self.updateAttackBoxStats(2, this.reverseStats);
                };
                if ((this.curFrame != null) && (this.curFrame > 1))
                {
                    if (this.curFrame > 50)
                    {
                    }
                    else if (this.curFrame > 35)
                    {
                        this.self.updateAttackStats({"air_ease":-1});
                    }
                    else if (this.curFrame > 24)
                    {
                        this.self.updateAttackStats({"air_ease":0});
                    };
                    this.self.stancePlayFrame(this.curFrame);
                };
            };
        }

        internal function frame2():*
        {
            if (this.curFrame != currentFrame)
            {
                this.self.setGlobalVariable("FalconPunchVFX", this.self.playVoiceSound(1));
            };
        }

        internal function frame3():*
        {
            if (this.curFrame != currentFrame)
            {
                this.charge = this.self.playAttackSound(1);
                this.self.setGlobalVariable("FalconPunchSFX", this.charge);
            };
        }

        internal function frame5():*
        {
            this.controls = this.self.getControls();
            if ((this.curFrame != currentFrame) && (this.self.isFacingRight() == this.controls.LEFT) && (this.controls.LEFT != this.controls.RIGHT))
            {
                this.self.stancePlayFrame("reversed");
            };
        }

        internal function frame24():*
        {
            if (this.curFrame != currentFrame)
            {
                this.self.attachEffect("global_dust_heavy");
            };
        }

        internal function frame25():*
        {
            if (this.curFrame == currentFrame)
            {
                this.killAttackboxes();
            }
            else
            {
                SSF2API.getCamera().shake(6);
                this.self.setGlobalVariable("FalconPunchVFX", this.self.playVoiceSound(2));
            };
            this.self.updateAttackStats({"air_ease":0});
        }

        internal function frame26():*
        {
            if (this.curFrame == currentFrame)
            {
                this.killAttackboxes();
            }
            else
            {
                this.checkAtkilled();
            };
        }

        internal function frame27():*
        {
            this.self.setXSpeed(8, false);
            SSF2API.stopSound(this.charge);
            if (this.curFrame == currentFrame)
            {
                this.killAttackboxes();
            }
            else
            {
                this.checkAtkilled();
                this.self.playAttackSound(2);
                this.self.setGlobalVariable("FalconPunchSFX", this.self.playAttackSound(3));
            };
        }

        internal function frame29():*
        {
            if (this.curFrame != currentFrame)
            {
                this.self.attachEffect("falconAfterEffect");
            };
        }

        internal function frame36():*
        {
            this.self.updateAttackStats({"air_ease":-1});
        }

        internal function frame51():*
        {
            this.self.destroyTimer(this.checkSpeckill);
            this.self.setGlobalVariable("FalconPunchReversed", false);
            this.self.setGlobalVariable("FalconPunchAtkID", null);
            this.self.setGlobalVariable("FalconPunchFrame", 0);
            this.self.endAttack();
        }

        internal function frame52():*
        {
            if (this.curFrame != currentFrame)
            {
                this.self.updateAttackBoxStats(1, this.reverseStats);
                this.self.updateAttackBoxStats(2, this.reverseStats);
                this.reversed = true;
            };
        }

        internal function frame56():*
        {
            if (this.curFrame != currentFrame)
            {
                this.self.flip();
            };
        }

        internal function frame61():*
        {
            this.self.stancePlayFrame("continue");
        }


    }
}

