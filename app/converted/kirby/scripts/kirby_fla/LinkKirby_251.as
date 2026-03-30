package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class LinkKirby_251 extends MovieClip
    {

        public var hatBox:MovieClip;
        public var hitBox:MovieClip;
        public var itemBox:MovieClip;
        public var self:KirbyExt;
        public var controls:Object;
        public var maxCharge:*;
        public var curCharge:*;
        public var hasBomb:Boolean;
        public var curItem:*;

        public function LinkKirby_251()
        {
            super();
            addFrameScript(0, this.frame1, 7, this.frame8, 12, this.frame13, 13, this.frame14, 18, this.frame19, 19, this.frame20, 30, this.frame31, 38, this.frame39, 43, this.frame44, 44, this.frame45, 46, this.frame47);
        }

        public function checkFire():void
        {
            this.controls = this.self.getControls();
            this.curCharge++;
            if (!this.controls.BUTTON1)
            {
                if (this.curCharge >= this.maxCharge)
                {
                    this.curCharge = this.maxCharge;
                };
                this.self.destroyTimer(this.checkFire);
                this.self.setGlobalVariable("LinkNSpecCharge", this.curCharge);
                this.self.stancePlayFrame("attack");
            };
        }

        public function checkSpeckill():void
        {
            if (!this.self.inState(CState.ATTACKING))
            {
                this.self.destroyTimer(this.checkSpeckill);
                this.self.setGlobalVariable("LinkNSpecCharge", 0);
                this.stopSFX();
            };
        }

        public function stopSFX():void
        {
            var _local_1:* = this.self.getGlobalVariable("LinkNSpecSFX");
            if (_local_1 != null)
            {
                SSF2API.stopSound(_local_1);
                this.self.setGlobalVariable("LinkNSpecSFX", null);
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
                this.curCharge = this.self.getGlobalVariable("LinkNSpecCharge");
                this.hasBomb = false;
                this.self.createTimer(1, -1, this.checkSpeckill, {"persistent":true});
                this.curItem = this.self.getItem();
                if ((this.curItem != null) && (this.curItem.getLinkageID() == "link_bomb"))
                {
                    this.hasBomb = true;
                };
                if (this.hasBomb)
                {
                    this.self.stancePlayFrame("bombArrow");
                };
            };
        }

        internal function frame8():*
        {
            this.self.setGlobalVariable("LinkNSpecSFX", this.self.playAttackSound(1));
            this.self.attachEffect("global_spark", {
                "x":this.flipX(35),
                "y":-20
            });
            this.self.attachEffect("global_dust_light");
        }

        internal function frame13():*
        {
            this.controls = this.self.getControls();
            if (!this.controls.BUTTON1)
            {
                this.self.setGlobalVariable("LinkNSpecCharge", 0);
                this.self.stancePlayFrame("attack");
            };
        }

        internal function frame14():*
        {
            this.self.createTimer(1, -1, this.checkFire);
        }

        internal function frame19():*
        {
            this.self.stancePlayFrame("loop1");
        }

        internal function frame20():*
        {
            this.stopSFX();
            this.self.playAttackSound(2);
            this.self.attachEffect("global_dust_heavy");
            if (this.hasBomb)
            {
                this.self.fireProjectile("nSpecBomb", 5, -19);
                this.self.attachEffect("bombArrowSpawn");
                this.self.removeItem();
            }
            else
            {
                this.self.fireProjectile("nSpecArrow", 5, -19);
                this.self.attachEffect("arrowSpawn");
            };
        }

        internal function frame31():*
        {
            this.self.endAttack();
        }

        internal function frame39():*
        {
            this.self.setGlobalVariable("LinkNSpecSFX", this.self.playAttackSound(1));
            this.self.attachEffect("global_dust_light");
        }

        internal function frame44():*
        {
            this.controls = this.self.getControls();
            if (!this.controls.BUTTON1)
            {
                this.self.setGlobalVariable("LinkNSpecCharge", 0);
                this.self.stancePlayFrame("attack");
            };
        }

        internal function frame45():*
        {
            this.self.createTimer(1, -1, this.checkFire);
        }

        internal function frame47():*
        {
            this.self.stancePlayFrame("loop2");
        }


    }
}

