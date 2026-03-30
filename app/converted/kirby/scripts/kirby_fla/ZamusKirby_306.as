package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class ZamusKirby_306 extends MovieClip
    {

        public var hatBox:MovieClip;
        public var hitBox:MovieClip;
        public var self:KirbyExt;
        public var controls:Object;
        public var maxCharge:*;
        public var curCharge:*;

        public function ZamusKirby_306()
        {
            super();
            addFrameScript(0, this.frame1, 10, this.frame11, 11, this.frame12, 16, this.frame17, 17, this.frame18, 30, this.frame31, 31, this.frame32, 32, this.frame33, 33, this.frame34);
        }

        public function checkFire():void
        {
            this.controls = this.self.getControls();
            this.curCharge++;
            if (this.curCharge >= this.maxCharge)
            {
                this.self.destroyTimer(this.checkFire);
                this.self.setGlobalVariable("ZamusNSpecCharge", this.maxCharge);
                this.self.stancePlayFrame("attack2");
            }
            else if (!this.controls.BUTTON1)
            {
                this.self.destroyTimer(this.checkFire);
                this.self.setGlobalVariable("ZamusNSpecCharge", this.curCharge);
                this.self.stancePlayFrame("attack");
            };
        }

        public function checkSpeckill():void
        {
            if (!this.self.inState(CState.ATTACKING))
            {
                this.self.destroyTimer(this.checkSpeckill);
                this.self.setGlobalVariable("ZamusNSpecCharge", 0);
                this.stopSFX();
            };
        }

        public function stopSFX():void
        {
            var _local_1:* = this.self.getGlobalVariable("ZamusNSpecSFX");
            if (_local_1 != null)
            {
                SSF2API.stopSound(_local_1);
                this.self.setGlobalVariable("ZamusNSpecSFX", null);
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
                this.curCharge = this.self.getGlobalVariable("ZamusNSpecCharge");
                this.self.createTimer(1, -1, this.checkSpeckill, {"persistent":true});
            };
        }

        internal function frame11():*
        {
            this.controls = this.self.getControls();
            if (!this.controls.BUTTON1)
            {
                this.self.setGlobalVariable("ZamusNSpecCharge", 0);
                this.self.stancePlayFrame("attack");
            };
        }

        internal function frame12():*
        {
            this.self.setGlobalVariable("ZamusNSpecSFX", this.self.playAttackSound(1));
            this.self.createTimer(1, -1, this.checkFire);
            this.self.attachEffect("global_spark", {
                "x":this.flipX(20),
                "y":-20
            });
            this.self.attachEffect("global_dust_swirl");
        }

        internal function frame17():*
        {
            this.self.stancePlayFrame("charging");
        }

        internal function frame18():*
        {
            this.self.fireProjectile("paralyzer_weak", 0, 0);
            this.self.attachEffect("global_dust_light");
            this.self.playAttackSound(2);
            this.stopSFX();
        }

        internal function frame31():*
        {
            this.self.destroyTimer(this.checkSpeckill);
            this.self.setGlobalVariable("ZamusNSpecCharge", 0);
        }

        internal function frame32():*
        {
            this.self.endAttack();
        }

        internal function frame33():*
        {
            this.self.fireProjectile("paralyzer_strong", 0, 0);
            this.self.attachEffect("global_dust_heavy");
            this.self.playAttackSound(3);
            this.stopSFX();
        }

        internal function frame34():*
        {
            this.self.stancePlayFrame("after");
        }


    }
}

