package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class MarthKirby_265 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:KirbyExt;
        public var controls:Object;
        public var maxCharge:*;
        public var curCharge:int;
        public var prepIt:*;
        public var sfx:*;
        public var dmg:*;
        public var tip:*;
        public var shld:*;
        public var spd:*;

        public function MarthKirby_265()
        {
            super();
            addFrameScript(0, this.frame1, 4, this.frame5, 5, this.frame6, 12, this.frame13, 13, this.frame14, 14, this.frame15, 15, this.frame16, 30, this.frame31);
        }

        public function checkFire():void
        {
            this.controls = this.self.getControls();
            this.curCharge++;
            if (!(this.controls.BUTTON1) || (this.curCharge >= this.maxCharge))
            {
                this.self.destroyTimer(this.checkFire);
                this.self.destroyTimer(this.checkSpeckill);
                this.stopSFX();
                this.self.stancePlayFrame("attack");
            };
        }

        public function checkSpeckill():void
        {
            if (!this.self.inState(CState.ATTACKING))
            {
                this.self.destroyTimer(this.checkSpeckill);
                this.stopSFX();
            };
        }

        public function stopSFX():void
        {
            if (this.sfx != null)
            {
                SSF2API.stopSound(this.sfx);
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
            if (SSF2API.isReady() && this.self)
            {
                this.controls = this.self.getControls();
                this.maxCharge = this.self.getAttackStat("chargetime_max");
                this.curCharge = 0;
                this.prepIt = false;
                this.self.playSound("marth_nspec_start");
            };
        }

        internal function frame5():*
        {
            this.controls = this.self.getControls();
            if (!this.controls.BUTTON1)
            {
                this.self.stancePlayFrame("attack");
            }
            else
            {
                this.sfx = this.self.playSound("marth_nspec_charge");
                this.self.createTimer(1, -1, this.checkSpeckill, {"persistent":true});
            };
        }

        internal function frame6():*
        {
            if (!this.prepIt)
            {
                this.prepIt = true;
                this.self.createTimer(1, -1, this.checkFire);
            };
            this.self.attachEffect("global_dust_heavy", {
                "scaleX":0.7,
                "scaleY":0.7
            });
        }

        internal function frame13():*
        {
            this.self.stancePlayFrame("charging");
        }

        internal function frame14():*
        {
            this.dmg = this.self.getAttackBoxStat(1, "damage");
            this.tip = this.self.getAttackBoxStat(2, "damage");
            this.shld = this.self.getAttackBoxStat(1, "shieldDamage");
            if (this.curCharge > this.maxCharge)
            {
                this.curCharge = this.maxCharge;
            };
            this.dmg += ((16 * this.curCharge) / this.maxCharge);
            this.tip += ((18 * this.curCharge) / this.maxCharge);
            this.shld += ((45 * this.curCharge) / this.maxCharge);
            this.self.updateAttackBoxStats(1, {
                "damage":this.dmg,
                "shieldDamage":this.shld
            });
            this.self.updateAttackBoxStats(2, {
                "damage":this.tip,
                "shieldDamage":this.shld
            });
            if (!this.self.isOnGround())
            {
                this.spd = (Math.abs(this.self.getXSpeed()) + ((18 * this.curCharge) / this.maxCharge));
                this.self.setXSpeed(this.spd, false);
            };
        }

        internal function frame15():*
        {
            this.self.addEffectToList(this.self.attachEffect("slash_marth_nspec", {
                "x":this.flipX(-20),
                "y":4.5,
                "scaleX":0.9,
                "scaleY":0.85,
                "parentLock":true,
                "syncHitStun":true
            }));
            this.self.clearEffectsOnStateChange();
        }

        internal function frame16():*
        {
            if (this.curCharge >= this.maxCharge)
            {
                this.self.playVoiceSound(1);
                this.self.playSound("marth_fspecU");
                this.self.playSound("marth_fspecD");
                this.self.playSound("marth_nspec1");
                this.self.attachEffect("ground_bounce", {"x":this.self.flipX(60)});
            }
            else
            {
                this.self.playSound("marth_fspecU");
                this.self.playSound("marth_nspec_swing");
            };
            this.self.attachEffect("global_dust_heavy");
            this.self.attachEffect("global_dust_swirl", {"x":this.self.flipX(-10)});
            this.self.attachEffect("global_spark", {
                "x":this.self.flipX(46),
                "y":-7
            });
            SSF2API.getCamera().shake(4);
        }

        internal function frame31():*
        {
            this.self.endAttack();
        }


    }
}

