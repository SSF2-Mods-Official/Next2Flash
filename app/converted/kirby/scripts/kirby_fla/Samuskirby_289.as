package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class Samuskirby_289 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var self:KirbyExt;
        public var controls:Object;
        public var maxCharge:int;
        public var curCharge:int;
        public var fullCharge:Boolean;
        public var boost:int;
        public var boostGuard:Boolean;
        public var speed:Number;
        public var onGround:*;
        public var press1B:Boolean;
        public var press2B:Boolean;
        public var press1S:Boolean;
        public var press2S:Boolean;
        public var press1L:Boolean;
        public var press2L:Boolean;
        public var press1R:Boolean;
        public var press2R:Boolean;

        public function Samuskirby_289()
        {
            super();
            addFrameScript(0, this.frame1, 7, this.frame8, 80, this.frame81, 81, this.frame82, 82, this.frame83, 96, this.frame97, 97, this.frame98, 112, this.frame113, 113, this.frame114, 114, this.frame115, 128, this.frame129, 129, this.frame130, 130, this.frame131, 144, this.frame145, 151, this.frame152);
        }

        public function checkPressed():void
        {
            this.controls = this.self.getControls();
            if (!this.controls.BUTTON1)
            {
                this.press1B = true;
            }
            else if (this.press1B)
            {
                this.press2B = true;
            };
            if (!this.controls.SHIELD)
            {
                this.press1S = true;
            }
            else if (this.press1S)
            {
                this.press2S = true;
            };
            if (!this.controls.LEFT)
            {
                this.press1L = true;
            }
            else if (this.press1L)
            {
                this.press2L = true;
            };
            if (!this.controls.RIGHT)
            {
                this.press1R = true;
            }
            else if (this.press1R)
            {
                this.press2R = true;
            };
        }

        public function checkControls():void
        {
            this.checkPressed();
            this.curCharge++;
            if (this.curCharge >= this.maxCharge)
            {
                this.self.destroyTimer(this.checkControls);
                this.self.destroyTimer(this.checkSpeckill);
                this.self.setGlobalVariable("SamusNSpecCharge", this.maxCharge);
                this.stopSFX();
                this.self.stancePlayFrame("finishCharge");
            }
            else if (this.press2B)
            {
                this.self.destroyTimer(this.checkControls);
                this.self.destroyTimer(this.checkSpeckill);
                this.self.setGlobalVariable("SamusNSpecCharge", this.curCharge);
                this.stopSFX();
                this.self.stancePlayFrame("attack");
            }
            else if (this.press2S)
            {
                this.self.destroyTimer(this.checkControls);
                this.self.destroyTimer(this.checkSpeckill);
                this.self.setGlobalVariable("SamusNSpecCharge", this.curCharge);
                this.stopSFX();
                this.self.endAttack();
            }
            else if (this.press2L && this.self.isOnGround())
            {
                this.self.destroyTimer(this.checkControls);
                this.self.destroyTimer(this.checkSpeckill);
                this.self.setGlobalVariable("SamusNSpecCharge", this.curCharge);
                this.stopSFX();
                this.self.faceLeft();
                this.self.toDodgeRoll();
            }
            else if (this.press2R && this.self.isOnGround())
            {
                this.self.destroyTimer(this.checkControls);
                this.self.destroyTimer(this.checkSpeckill);
                this.self.setGlobalVariable("SamusNSpecCharge", this.curCharge);
                this.stopSFX();
                this.self.faceRight();
                this.self.toDodgeRoll();
            };
        }

        public function checkSpeckill():void
        {
            if (!this.self.inState(CState.ATTACKING))
            {
                this.self.destroyTimer(this.checkSpeckill);
                this.self.setGlobalVariable("SamusNSpecCharge", 0);
                if (!this.boostGuard)
                {
                    this.self.setGlobalVariable("SamusNSpecBoost", 0);
                };
                this.stopSFX();
            };
        }

        public function fireAir(_arg_1:*=null):*
        {
            this.self.destroyTimer(this.checkControls);
            this.self.destroyTimer(this.checkSpeckill);
            this.self.removeEventListener(SSF2Event.GROUND_LEAVE, this.fireAir);
            this.stopSFX();
            this.onGround = false;
            this.self.updateAttackStats({"canFallOff":true});
            if (this.curCharge >= this.maxCharge)
            {
                this.curCharge = (this.maxCharge - 1);
            };
            this.self.setGlobalVariable("SamusNSpecCharge", this.curCharge);
            this.self.stancePlayFrame("attackAir");
        }

        public function stopSFX():void
        {
            var _local_1:* = this.self.getGlobalVariable("SamusNSpecSFX");
            if (_local_1 != null)
            {
                SSF2API.stopSound(_local_1);
                this.self.setGlobalVariable("SamusNSpecSFX", null);
            };
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.controls = this.self.getControls();
                this.maxCharge = this.self.getAttackStat("chargetime_max");
                this.curCharge = this.self.getGlobalVariable("SamusNSpecCharge");
                this.fullCharge = (this.curCharge >= this.maxCharge);
                this.boost = this.self.getGlobalVariable("SamusNSpecBoost");
                this.boostGuard = false;
                this.speed = 0;
                this.onGround = this.self.isOnGround();
                this.self.createTimer(1, -1, this.checkSpeckill, {"persistent":true});
                if (this.onGround)
                {
                    if (this.fullCharge)
                    {
                        this.self.setGlobalVariable("SamusNSpecBoost", this.maxCharge);
                        this.boostGuard = true;
                    }
                    else
                    {
                        this.self.setGlobalVariable("SamusNSpecBoost", 0);
                        this.self.createTimer(1, -1, this.checkPressed);
                        this.self.addEventListener(SSF2Event.GROUND_LEAVE, this.fireAir);
                    };
                }
                else
                {
                    this.self.updateAttackStats({"canFallOff":true});
                    this.boostGuard = true;
                    if (this.boost > 0)
                    {
                        this.speed = ((((this.boost * 6) / this.maxCharge) + 3.2) * -1);
                        this.self.setGlobalVariable("SamusNSpecBoost", 0);
                    }
                    else
                    {
                        this.speed = ((((this.curCharge * 6) / this.maxCharge) + 3.2) * -1);
                        this.self.setGlobalVariable("SamusNSpecBoost", this.curCharge);
                    };
                };
            };
            this.press1B = false;
            this.press2B = false;
            this.press1S = false;
            this.press2S = false;
            this.press1L = false;
            this.press2L = false;
            this.press1R = false;
            this.press2R = false;
        }

        internal function frame8():*
        {
            SSF2API.print(("chargeTime: " + this.curCharge));
            if (this.onGround)
            {
                this.self.destroyTimer(this.checkPressed);
                if (this.fullCharge)
                {
                    this.self.destroyTimer(this.checkSpeckill);
                    this.self.stancePlayFrame("attack2");
                }
                else if (this.press2B)
                {
                    this.self.destroyTimer(this.checkSpeckill);
                    this.self.setGlobalVariable("SamusNSpecCharge", this.curCharge);
                    this.self.stancePlayFrame("attack");
                }
                else
                {
                    this.self.setGlobalVariable("SamusNSpecSFX", this.self.playAttackSound(1));
                    this.self.createTimer(1, -1, this.checkControls);
                    if (this.curCharge > 0)
                    {
                        this.self.stancePlayFrame((currentFrame + this.curCharge));
                    };
                };
            }
            else
            {
                this.self.destroyTimer(this.checkSpeckill);
                if (this.fullCharge)
                {
                    this.self.stancePlayFrame("attackAir2");
                }
                else
                {
                    this.self.stancePlayFrame("attackAir");
                };
            };
        }

        internal function frame81():*
        {
            this.self.stancePlayFrame("loop");
        }

        internal function frame82():*
        {
            this.self.removeEventListener(SSF2Event.GROUND_LEAVE, this.fireAir);
            this.self.fireProjectile("unchargedshot", 14, -15);
            SSF2API.getCamera().shake(3);
            this.self.playAttackSound(2);
            this.self.setGlobalVariable("SamusNSpecBoost", this.curCharge);
        }

        internal function frame83():*
        {
            this.self.attachEffect("global_dust_light");
        }

        internal function frame97():*
        {
            this.self.endAttack();
        }

        internal function frame98():*
        {
            this.self.fireProjectile("chargedshot", 14, -15);
            this.self.attachEffect("global_dust_heavy");
            SSF2API.getCamera().shake(8);
            this.self.playAttackSound(5);
        }

        internal function frame113():*
        {
            this.self.endAttack();
        }

        internal function frame114():*
        {
            this.self.fireProjectile("unchargedshot", 14, -15);
            this.self.setXSpeed(this.speed, false);
            this.self.setYSpeed(-3);
            SSF2API.getCamera().shake(3);
            this.self.playAttackSound(2);
        }

        internal function frame115():*
        {
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.self.toHeavyLand);
        }

        internal function frame129():*
        {
            this.self.endAttack();
        }

        internal function frame130():*
        {
            this.self.fireProjectile("chargedshot", 14, -15);
            this.self.setXSpeed(this.speed, false);
            this.self.setYSpeed(-5);
            SSF2API.getCamera().shake(8);
            this.self.playAttackSound(5);
        }

        internal function frame131():*
        {
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.self.toHeavyLand);
        }

        internal function frame145():*
        {
            this.self.endAttack();
        }

        internal function frame152():*
        {
            this.self.endAttack();
        }


    }
}

