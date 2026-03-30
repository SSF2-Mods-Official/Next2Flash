package simon_fla
{
    import flash.display.MovieClip;

    public dynamic class Jab_22 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var self:SimonExt;
        public var whipSpin:*;
        public var proj:*;
        public var speed:*;
        public var rotVal:*;
        public var offsetX:*;
        public var offsetY:*;
        public var minTime:*;
        public var soundCounter:*;
        public var prevScale:*;
        public var scaleDiff:*;

        public function Jab_22()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 3, this.frame4, 5, this.frame6, 7, this.frame8, 9, this.frame10, 11, this.frame12, 13, this.frame14, 15, this.frame16, 17, this.frame18, 24, this.frame25);
        }

        public function checkControls(_arg_1:*=null):*
        {
            var _local_2:* = this.self.getControls();
        }

        public function updateWhipSpin(_arg_1:*=null):*
        {
            if (this.proj && !(this.proj.isDisposed()))
            {
                this.proj.setX((this.self.getX() + (this.self.flipX((29 + this.offsetX)) * this.self.getScale().x)));
                this.proj.setY((this.self.getY() - ((41.5 + this.offsetY) * this.self.getScale().y)));
                if (this.prevScale && (this.self.getScale().x != this.prevScale))
                {
                    SSF2API.print((this.self.getScale().x / this.prevScale).toString());
                    SSF2API.print(this.proj.getScale().x.toString());
                    SSF2API.print((this.proj.getScale().x * (this.self.getScale().x / this.prevScale)).toString());
                    this.proj.setScale(this.self.flipX((this.proj.getScale().x * (this.self.getScale().x / (this.prevScale * this.prevScale)))), (this.proj.getScale().y * (this.self.getScale().y / (this.prevScale * this.prevScale))));
                };
                this.prevScale = this.self.getScale().x;
                if ((!this.self.getControls().RIGHT && !this.self.getControls().LEFT && (this.minTime == 0)) || (this.self.getControls().RIGHT && this.self.getControls().LEFT && (this.minTime == 0)))
                {
                    if (((this.speed > 0) && (this.rotVal > 0) && (this.rotVal <= 180)) || ((this.speed < 0) && (this.rotVal > 180) && (this.rotVal < 360)))
                    {
                        this.speed *= 0.8;
                    };
                };
                if ((this.rotVal > 2) && (this.rotVal <= 180))
                {
                    this.speed -= 0.8;
                }
                else if ((this.rotVal < 358) && (this.rotVal > 180))
                {
                    this.speed += 0.8;
                };
                if ((this.speed < 1) && (this.speed > -1))
                {
                    if ((this.rotVal > 359) || (this.rotVal < 1))
                    {
                        this.speed = 0;
                        this.rotVal = 0;
                    };
                };
                if (this.speed > 24)
                {
                    this.speed -= 1.6;
                }
                else if (this.speed < -24)
                {
                    this.speed += 1.6;
                };
                if ((this.speed < 24) && this.self.getControls().LEFT)
                {
                    this.speed += 2.4;
                };
                if ((this.speed > -24) && this.self.getControls().RIGHT)
                {
                    this.speed -= 2.4;
                };
                this.rotVal += this.speed;
                if (this.rotVal < 0)
                {
                    this.rotVal += 360;
                }
                else if (this.rotVal > 360)
                {
                    this.rotVal -= 360;
                };
                gotoAndStop(((Math.floor((this.rotVal / 45)) * 2) + this.whipSpin));
                if (this.self.isFacingRight())
                {
                    if (this.speed > 8)
                    {
                        this.proj.getStanceMC().gotoAndStop(10);
                    }
                    else if (this.speed < -8)
                    {
                        this.proj.getStanceMC().gotoAndStop(4);
                    }
                    else if (this.speed > 1)
                    {
                        this.proj.getStanceMC().gotoAndStop(8);
                    }
                    else if (this.speed < -1)
                    {
                        this.proj.getStanceMC().gotoAndStop(6);
                    }
                    else
                    {
                        this.proj.getStanceMC().gotoAndStop(2);
                    };
                }
                else if (this.speed > 8)
                {
                    this.proj.getStanceMC().gotoAndStop(4);
                }
                else if (this.speed < -8)
                {
                    this.proj.getStanceMC().gotoAndStop(10);
                }
                else if (this.speed > 1)
                {
                    this.proj.getStanceMC().gotoAndStop(6);
                }
                else if (this.speed < -1)
                {
                    this.proj.getStanceMC().gotoAndStop(8);
                }
                else
                {
                    this.proj.getStanceMC().gotoAndStop(2);
                };
                if ((this.speed > 16) || (this.speed < -16))
                {
                    if (this.soundCounter < 13)
                    {
                        this.soundCounter++;
                    }
                    else
                    {
                        this.self.playSound("ssf2_snd_sfx_simon_attack_swing_s");
                        SSF2API.print(((this.self.getScale().x.toString() + " ") + this.proj.getScale().x.toString()));
                        this.soundCounter = 0;
                    };
                }
                else
                {
                    this.soundCounter = 13;
                };
                this.proj.updateAttackBoxStats(1, {
                    "direction":60,
                    "damage":((2 + (Math.abs(this.speed) / 12)) + Math.floor((Math.abs(this.speed) / 10))),
                    "power":(Math.abs(this.speed) * 1.4),
                    "kbConstant":60
                });
                this.proj.setRotation((int((this.rotVal / 22.5)) * 22.5));
                if (this.minTime > 0)
                {
                    this.minTime--;
                }
                else if (!this.self.getControls().BUTTON2)
                {
                    this.proj.destroy();
                    gotoAndStop("endlag");
                };
            };
        }

        public function cleanup(_arg_1:*=null):*
        {
            if (this.proj && !(this.proj.isDisposed()))
            {
                this.proj.destroy();
            };
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as SimonExt);
            this.whipSpin = 4;
            this.speed = 0;
            this.rotVal = 0;
            this.offsetX = 0;
            this.offsetY = 0;
            this.minTime = 7;
            this.soundCounter = 0;
        }

        internal function frame3():*
        {
            this.self.attachEffect("global_dust_light");
            this.self.playAttackSound(1);
            gotoAndStop(this.whipSpin);
            this.proj = this.self.fireProjectile("jab_whip");
            this.self.addEventListener(SSF2Event.STATE_CHANGE, this.cleanup);
            if (this.self.isFacingRight())
            {
                this.speed = -40;
            }
            else
            {
                this.speed = 40;
            };
            this.self.createTimer(1, -1, this.updateWhipSpin);
        }

        internal function frame4():*
        {
            this.offsetX = 0;
            this.offsetY = 0;
        }

        internal function frame6():*
        {
            this.offsetX = 0;
            this.offsetY = 0;
        }

        internal function frame8():*
        {
            this.offsetX = 1;
            this.offsetY = 1;
        }

        internal function frame10():*
        {
            this.offsetX = 3;
            this.offsetY = 1;
        }

        internal function frame12():*
        {
            this.offsetX = 3;
            this.offsetY = 1;
        }

        internal function frame14():*
        {
            this.offsetX = 3;
            this.offsetY = 1;
        }

        internal function frame16():*
        {
            this.offsetX = 1;
            this.offsetY = 1;
        }

        internal function frame18():*
        {
            this.offsetX = 0;
            this.offsetY = 0;
        }

        internal function frame25():*
        {
            this.self.endAttack();
        }


    }
}

