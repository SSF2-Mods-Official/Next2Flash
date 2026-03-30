package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class SheikKirby_297 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:KirbyExt;
        public var num_needles:int;
        public var xframe:*;
        public var charge:*;
        public var rand:*;
        public var proj:*;
        public var sheik_ground:Boolean;

        public function SheikKirby_297()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 6, this.frame7, 7, this.frame8, 11, this.frame12, 15, this.frame16, 16, this.frame17, 19, this.frame20, 20, this.frame21, 33, this.frame34);
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
            this.rand = 0;
            if (parent && SSF2API.isReady() && this.self)
            {
                this.sheik_ground = this.self.isOnGround();
                if (!this.sheik_ground)
                {
                    this.self.forceAttack("kirby_sheik_air", null, true);
                };
            };
        }

        internal function frame3():*
        {
            this.self.attachEffect("global_dust_light");
        }

        internal function frame7():*
        {
            this.xframe = "charging";
        }

        internal function frame8():*
        {
            this.self.playAttackSound(1);
        }

        internal function frame12():*
        {
            this.self.attachEffect("global_dust_light");
        }

        internal function frame16():*
        {
            this.self.stancePlayFrame("charging");
        }

        internal function frame17():*
        {
            this.xframe = "attack";
            this.charge = this.self.getAttackStat("chargetime");
            this.num_needles = ((this.charge / 10) + 1);
            this.self.attachEffect("global_dust_light");
            this.self.playVoiceSound(1);
        }

        internal function frame20():*
        {
            this.num_needles--;
            this.self.fireProjectile("needle", 0, 20);
        }

        internal function frame21():*
        {
            if (this.num_needles <= 0)
            {
                this.self.stancePlayFrame("finish");
            }
            else
            {
                this.self.stancePlayFrame("loop");
            };
        }

        internal function frame34():*
        {
            this.self.endAttack();
        }


    }
}

