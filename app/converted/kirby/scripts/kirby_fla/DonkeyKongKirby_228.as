package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class DonkeyKongKirby_228 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:KirbyExt;
        public var controls:Object;
        public var maxCharge:int;
        public var curCharge:int;
        public var fullCharge:Boolean;
        public var grounded:Boolean;
        public var prepIt:Boolean;
        public var doIt:Boolean;
        public var dmg:Number;
        public var press1B:Boolean;
        public var press2B:Boolean;
        public var press1S:Boolean;
        public var press2S:Boolean;
        public var press1L:Boolean;
        public var press2L:Boolean;
        public var press1R:Boolean;
        public var press2R:Boolean;

        public function DonkeyKongKirby_228()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 6, this.frame7, 9, this.frame10, 10, this.frame11, 16, this.frame17, 18, this.frame19, 19, this.frame20, 41, this.frame42, 42, this.frame43, 47, this.frame48, 48, this.frame49, 49, this.frame50, 50, this.frame51, 51, this.frame52, 52, this.frame53, 66, this.frame67);
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
                this.self.setGlobalVariable("DKNSpecCharge", this.maxCharge);
                this.self.createChargeEffect("dong");
                this.self.endAttack();
            }
            else if (this.press2B)
            {
                this.self.destroyTimer(this.checkControls);
                this.self.stancePlayFrame("attack");
            }
            else if (this.press2S)
            {
                this.self.destroyTimer(this.checkControls);
                this.self.destroyTimer(this.checkSpeckill);
                this.self.setGlobalVariable("DKNSpecCharge", this.curCharge);
                this.self.endAttack();
            }
            else if (this.press2L && this.self.isOnGround())
            {
                this.self.destroyTimer(this.checkControls);
                this.self.destroyTimer(this.checkSpeckill);
                this.self.setGlobalVariable("DKNSpecCharge", this.curCharge);
                this.self.faceLeft();
                this.self.toDodgeRoll();
            }
            else if (this.press2R && this.self.isOnGround())
            {
                this.self.destroyTimer(this.checkControls);
                this.self.destroyTimer(this.checkSpeckill);
                this.self.setGlobalVariable("DKNSpecCharge", this.curCharge);
                this.self.faceRight();
                this.self.toDodgeRoll();
            };
        }

        public function checkSpeckill():void
        {
            if (!this.self.inState(CState.ATTACKING))
            {
                this.self.destroyTimer(this.checkSpeckill);
                this.self.setGlobalVariable("DKNSpecCharge", 0);
                this.self.removeChargeEffect("dong");
            };
        }

        public function checkGround(_arg_1:*=null):*
        {
            if (this.grounded && !(this.self.isOnGround()))
            {
                if (this.doIt)
                {
                    this.grounded = false;
                }
                else
                {
                    this.self.destroyTimer(this.checkControls);
                    this.self.destroyTimer(this.checkSpeckill);
                    this.self.setGlobalVariable("DKNSpecCharge", this.curCharge);
                    this.self.endAttack();
                };
            }
            else if (!(this.grounded) && this.self.isOnGround())
            {
                this.grounded = true;
            };
        }

        public function flipX(_arg_1:Number):Number
        {
            if (this.self.isFacingRight())
            {
                return _arg_1;
            };
            return _arg_1 * -1;
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.controls = this.self.getControls();
                this.maxCharge = this.self.getAttackStat("chargetime_max");
                this.curCharge = this.self.getGlobalVariable("DKNSpecCharge");
                this.fullCharge = (this.curCharge >= this.maxCharge);
                this.grounded = this.self.isOnGround();
                this.prepIt = false;
                this.doIt = false;
                this.dmg = 0;
                this.self.createTimer(1, -1, this.checkSpeckill, {"persistent":true});
                this.self.createTimer(1, -1, this.checkGround);
                if (this.fullCharge)
                {
                    this.self.stancePlayFrame("attack2");
                }
                else
                {
                    this.self.createTimer(1, -1, this.checkPressed);
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

        internal function frame4():*
        {
            if (this.prepIt)
            {
                this.self.playAttackSound(1);
                this.self.attachEffect("global_dust_light");
            }
            else
            {
                this.self.destroyTimer(this.checkPressed);
                if (this.press2B)
                {
                    this.self.stancePlayFrame("attack");
                }
                else
                {
                    this.prepIt = true;
                    this.self.playAttackSound(1);
                    this.self.attachEffect("global_dust_light");
                    this.self.createTimer(1, -1, this.checkControls);
                };
            };
        }

        internal function frame7():*
        {
            this.self.attachEffect("global_spark", {
                "x":this.flipX(-30),
                "y":-20
            });
        }

        internal function frame10():*
        {
            this.self.stancePlayFrame("charging");
        }

        internal function frame11():*
        {
            this.doIt = true;
        }

        internal function frame17():*
        {
            this.self.attachEffect("global_dust_heavy");
        }

        internal function frame19():*
        {
            this.self.playAttackSound(2);
            this.self.playSound("dk_nspecial_swing");
        }

        internal function frame20():*
        {
            this.dmg = this.self.getAttackBoxStat(1, "damage");
            if (!this.grounded)
            {
                this.dmg -= 3;
            };
            this.dmg += ((18 * this.curCharge) / this.maxCharge);
            this.self.updateAttackBoxStats(1, {"damage":this.dmg});
            this.self.updateAttackStats({"allowControl":true});
            this.self.attachEffect("global_dust_blast", {
                "x":this.self.flipX(55),
                "y":-17,
                "scaleX":1.1,
                "scaleY":1.1,
                "parentLock":true
            });
            SSF2API.getCamera().shake(7);
        }

        internal function frame42():*
        {
            this.self.endAttack();
        }

        internal function frame43():*
        {
            this.doIt = true;
            this.self.removeChargeEffect("dong");
        }

        internal function frame48():*
        {
            this.self.attachEffect("dk_shockwave");
            this.self.attachEffect("global_dust_heavy");
            if (this.grounded)
            {
                this.self.updateAttackStats({"superArmor":true});
            };
        }

        internal function frame49():*
        {
            if (this.grounded)
            {
                this.self.updateAttackStats({"superArmor":true});
            };
        }

        internal function frame50():*
        {
            if (this.grounded)
            {
                this.self.updateAttackStats({"superArmor":true});
            };
        }

        internal function frame51():*
        {
            this.self.playVoiceSound(1);
            this.self.playAttackSound(2);
            this.self.playSound("dk_nspecial_swing");
            this.self.attachEffect("global_dust_heavy");
            this.self.updateAttackStats({"superArmor":true});
        }

        internal function frame52():*
        {
            if (this.grounded)
            {
                this.dmg = 28;
            }
            else
            {
                this.dmg = 25;
            };
            this.self.updateAttackBoxStats(1, {
                "damage":this.dmg,
                "power":10,
                "kbConstant":90
            });
            this.self.updateAttackStats({"allowControl":true});
            this.self.attachEffect("global_dust_blast", {
                "x":this.self.flipX(55),
                "y":-17,
                "scaleX":1.1,
                "scaleY":1.1,
                "parentLock":true
            });
            SSF2API.getCamera().shake(7);
        }

        internal function frame53():*
        {
            this.self.updateAttackStats({"superArmor":false});
        }

        internal function frame67():*
        {
            this.self.endAttack();
        }


    }
}

