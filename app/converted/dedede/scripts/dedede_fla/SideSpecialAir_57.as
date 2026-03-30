package dedede_fla
{
    import flash.display.MovieClip;

    public dynamic class SideSpecialAir_57 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var gordo:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var itemBox:MovieClip;
        public var self:DededeExt;
        public var gordoReady:Boolean;

        public function SideSpecialAir_57()
        {
            super();
            addFrameScript(0, this.frame1, 5, this.frame6, 13, this.frame14, 15, this.frame16, 30, this.frame31);
        }

        public function toGround(_arg_1:*=null):*
        {
            this.self.setGlobalVariable("DaymanSSpecFrame", currentFrame);
            this.self.setGlobalVariable("DaymanSSpecReady", this.gordoReady);
            this.self.setGlobalVariable("DaymanSSpecAtkID", this.self.getAttackStat("atk_id"));
            this.self.forceAttack("b_forward", null, true);
        }

        public function gordoHide(_arg_1:*=null):*
        {
            if (currentFrame > 15)
            {
                this.self.destroyTimer(this.gordoHide);
            }
            else if (currentFrame >= 3)
            {
                this.gordo.visible = false;
            };
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as DededeExt);
            this.gordoReady = false;
            if (SSF2API.isReady() && this.self)
            {
                if ((this.self.gordo == null) || this.self.gordo.isDisposed())
                {
                    this.gordoReady = true;
                }
                else
                {
                    this.self.createTimer(1, -1, this.gordoHide);
                };
                this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.toGround);
            };
        }

        internal function frame6():*
        {
            if (this.gordoReady)
            {
                this.self.playSound("ssf2_snd_sfx_dedede_fspec_spawn");
            };
        }

        internal function frame14():*
        {
            if (this.gordoReady)
            {
                this.self.playSound("ssf2_snd_sfx_dedede_fspec_launch");
            }
            else
            {
                this.self.playSound("ssf2_snd_sfx_dedede_swing_m");
            };
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(-10),
                "y":3,
                "scaleX":-0.5,
                "scaleY":-0.5
            });
        }

        internal function frame16():*
        {
            if (this.gordoReady)
            {
                this.self.gordo = this.self.fireProjectile("dedede_gordo", 0, -25);
                this.self.gordo.safeMove(this.self.flipX(60), 0);
            };
        }

        internal function frame31():*
        {
            this.self.endAttack();
        }


    }
}

