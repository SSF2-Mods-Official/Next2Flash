package gameandwatch_fla
{
    import flash.display.MovieClip;

    public dynamic class USpecial_41 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hand:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:gameandwatchExt;
        public var oldSpeed:Number;
        public var testSpeed:Number;
        public var previousSpeed:Number;
        public var hSpeed:Number;
        public var canDrop:*;

        public function USpecial_41()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 3, this.frame4, 4, this.frame5, 5, this.frame6, 6, this.frame7, 7, this.frame8, 8, this.frame9, 9, this.frame10, 10, this.frame11, 11, this.frame12, 12, this.frame13, 13, this.frame14, 14, this.frame15, 15, this.frame16, 16, this.frame17, 17, this.frame18, 19, this.frame20, 23, this.frame24, 34, this.frame35, 62, this.frame63, 74, this.frame75, 75, this.frame76);
        }

        public function restoreSpecials(_arg_1:*=null):void
        {
            SSF2API.print("gw: Restoring specials");
            this.self.setAttackEnabled(true, "b_up");
            this.self.setAttackEnabled(true, "b_up_air");
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.restoreSpecials);
            this.self.removeEventListener(SSF2Event.CHAR_HURT, this.restoreSpecials);
            this.self.removeEventListener(SSF2Event.CHAR_GRABBED, this.restoreSpecials);
            this.self.removeEventListener(SSF2Event.CHAR_LEDGE_GRAB, this.restoreSpecials);
        }

        public function iasa():*
        {
            this.self.updateAttackStats({
                "airCancel":true,
                "airCancelSpecial":true
            });
        }

        public function checkDrop():*
        {
            if (this.canDrop && this.self.getControls().DOWN)
            {
                this.self.endAttack();
                this.self.playSound("gw_usmash");
            };
            if (!this.self.getControls().DOWN)
            {
                this.canDrop = true;
            };
        }

        public function speedTest():*
        {
            this.testSpeed = this.self.getXSpeed();
            if (this.testSpeed != this.previousSpeed)
            {
                SSF2API.print(this.testSpeed.toString());
            };
            this.previousSpeed = this.testSpeed;
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as gameandwatchExt);
            this.oldSpeed = 0;
            this.testSpeed = 0;
            this.previousSpeed = 0;
            this.hSpeed = 1.3;
            if (this.self && SSF2API.isReady())
            {
                this.canDrop = false;
                this.self.setAttackEnabled(false, "b_up", 999);
                this.self.setAttackEnabled(false, "b_up_air", 999);
                this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.restoreSpecials, {"persistent":true});
                this.self.addEventListener(SSF2Event.CHAR_HURT, this.restoreSpecials, {"persistent":true});
                this.self.addEventListener(SSF2Event.CHAR_GRABBED, this.restoreSpecials, {"persistent":true});
                this.self.addEventListener(SSF2Event.CHAR_LEDGE_GRAB, this.restoreSpecials, {"persistent":true});
                this.self.fireProjectile("firemen");
                this.self.playSound("beep_low_mid");
                this.oldSpeed = this.self.getXSpeed();
                SSF2API.print(this.oldSpeed.toString());
                this.self.resetMovement();
            };
        }

        internal function frame3():*
        {
            this.self.createTimer(1, 0, this.speedTest);
            this.self.attachEffect("global_dust_cloud");
        }

        internal function frame4():*
        {
            this.self.setYSpeed(-25);
            if (this.self.getControls().RIGHT && this.self.isFacingRight())
            {
                this.self.setXSpeed(((this.oldSpeed * 0.4) + (this.hSpeed * 3)));
            }
            else if (this.self.getControls().LEFT && this.self.isFacingRight())
            {
                this.self.setXSpeed(((this.oldSpeed * 0.4) - (this.hSpeed * 3)));
            }
            else if (this.self.getControls().RIGHT && !(this.self.isFacingRight()))
            {
                this.self.setXSpeed(((this.oldSpeed * 0.4) + (this.hSpeed * 3)));
            }
            else if (this.self.getControls().LEFT && !(this.self.isFacingRight()))
            {
                this.self.setXSpeed(((this.oldSpeed * 0.4) - (this.hSpeed * 3)));
            };
            this.self.playSound("gw_usmash");
            this.self.updateAttackBoxStats(1, {"power":112});
        }

        internal function frame5():*
        {
            this.self.setYSpeed(-25);
            this.self.updateAttackBoxStats(1, {"power":104});
        }

        internal function frame6():*
        {
            this.self.setYSpeed(-25);
            this.self.updateAttackBoxStats(1, {"power":93});
        }

        internal function frame7():*
        {
            this.self.setYSpeed(-25);
            this.self.updateAttackBoxStats(1, {"power":84});
        }

        internal function frame8():*
        {
            this.self.setYSpeed(-25);
            this.self.updateAttackBoxStats(1, {
                "power":75,
                "hitLag":14
            });
        }

        internal function frame9():*
        {
            this.self.setYSpeed(-25);
            this.self.updateAttackBoxStats(1, {
                "power":53,
                "hitLag":13
            });
        }

        internal function frame10():*
        {
            this.self.setYSpeed(-20);
            this.self.updateAttackBoxStats(1, {
                "power":35,
                "hitLag":12
            });
        }

        internal function frame11():*
        {
            this.self.setYSpeed(-10);
            this.self.updateAttackBoxStats(1, {
                "power":30,
                "hitLag":11
            });
        }

        internal function frame12():*
        {
            this.self.setYSpeed(-9);
            this.self.updateAttackBoxStats(1, {"hitLag":10});
        }

        internal function frame13():*
        {
            this.self.setYSpeed(-8);
            this.self.updateAttackBoxStats(1, {"hitLag":9});
        }

        internal function frame14():*
        {
            this.self.setYSpeed(-7);
            this.self.updateAttackBoxStats(1, {"hitLag":8});
        }

        internal function frame15():*
        {
            this.self.setYSpeed(-6);
            this.self.updateAttackBoxStats(1, {"hitLag":7});
        }

        internal function frame16():*
        {
            this.self.setYSpeed(-5);
            this.self.updateAttackBoxStats(1, {"hitLag":6});
        }

        internal function frame17():*
        {
            this.self.setYSpeed(-5);
            this.self.updateAttackStats({"allowControl":true});
            this.self.createTimer(1, 0, this.checkDrop);
            this.iasa();
        }

        internal function frame18():*
        {
            this.self.setYSpeed(-3);
        }

        internal function frame20():*
        {
            this.self.playSound("gw_usmash");
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.self.toHeavyLand);
        }

        internal function frame24():*
        {
            this.self.playSound("snd_se_GW_Wave03_Hi");
            this.self.updateAttackStats({
                "xSpeedAccelAir":0.6,
                "xSpeedCap":7.4
            });
        }

        internal function frame35():*
        {
            if (this.self.isFacingRight())
            {
                this.self.setXSpeed((this.self.getXSpeed() + this.hSpeed));
            }
            else
            {
                this.self.setXSpeed((this.self.getXSpeed() - this.hSpeed));
            };
        }

        internal function frame63():*
        {
            if (this.self.isFacingRight())
            {
                this.self.setXSpeed((this.self.getXSpeed() - this.hSpeed));
            }
            else
            {
                this.self.setXSpeed((this.self.getXSpeed() + this.hSpeed));
            };
        }

        internal function frame75():*
        {
            this.self.stancePlayFrame("loop");
        }

        internal function frame76():*
        {
            this.self.endAttack();
        }


    }
}

