package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class IchigoKirby_243 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var self:KirbyExt;
        public var controls:Object;
        public var maxCharge:*;
        public var curCharge:int;
        public var prepIt:*;

        public function IchigoKirby_243()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 4, this.frame5, 8, this.frame9, 9, this.frame10, 13, this.frame14, 14, this.frame15, 16, this.frame17, 17, this.frame18, 40, this.frame41);
        }

        public function checkFire():void
        {
            this.controls = this.self.getControls();
            this.curCharge++;
            if (!(this.controls.BUTTON1) || (this.curCharge >= this.maxCharge))
            {
                this.self.destroyTimer(this.checkFire);
                this.self.setGlobalVariable("IchigoNSpecCharge", this.curCharge);
                this.self.stancePlayFrame("attack");
            };
        }

        public function checkSpeckill():void
        {
            if (!this.self.inState(CState.ATTACKING))
            {
                this.self.destroyTimer(this.checkSpeckill);
                this.self.setGlobalVariable("IchigoNSpecCharge", 0);
            };
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.controls = this.self.getControls();
                this.maxCharge = this.self.getAttackStat("chargetime_max");
                this.curCharge = 0;
                this.prepIt = false;
                this.self.createTimer(1, -1, this.checkSpeckill, {"persistent":true});
                this.self.playVoiceSound(1);
                if (!this.self.isOnGround())
                {
                    this.self.updateAttackStats({
                        "xSpeedDecayAir":-0.3,
                        "allowControlGround":false
                    });
                };
            };
        }

        internal function frame4():*
        {
            this.self.addEffectToList(this.self.pushEffectBehind(this.self.attachEffect("ichigo_nspec_back", {
                "scaleX":1.22,
                "scaleY":1.22,
                "parentLock":true
            })));
            this.self.addEffectToList(this.self.attachEffect("ichigo_nspec_front", {
                "scaleX":1.22,
                "scaleY":1.22,
                "parentLock":true
            }));
            this.self.clearEffectsOnStateChange();
        }

        internal function frame5():*
        {
            this.self.playAttackSound(2);
        }

        internal function frame9():*
        {
            this.controls = this.self.getControls();
            if (!this.controls.BUTTON1)
            {
                this.self.stancePlayFrame("attack");
            };
        }

        internal function frame10():*
        {
            if (!this.prepIt)
            {
                this.prepIt = true;
                this.self.createTimer(1, -1, this.checkFire);
            };
        }

        internal function frame14():*
        {
            this.self.stancePlayFrame("charging");
        }

        internal function frame15():*
        {
            this.self.playVoiceSound(2);
        }

        internal function frame17():*
        {
            this.self.playAttackSound(1);
            this.self.attachEffect("global_dust_heavy");
            if (!this.self.isOnGround())
            {
                this.self.setYSpeed(-5);
            };
        }

        internal function frame18():*
        {
            this.self.fireProjectile("getsuga2");
        }

        internal function frame41():*
        {
            this.self.endAttack();
        }


    }
}

