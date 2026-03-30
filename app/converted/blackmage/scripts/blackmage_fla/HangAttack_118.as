package blackmage_fla
{
    import flash.display.MovieClip;

    public dynamic class HangAttack_118 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;

        public function HangAttack_118()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 9, this.frame10, 10, this.frame11, 11, this.frame12, 12, this.frame13, 24, this.frame25);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
            if (parent && SSF2API.isReady())
            {
                this.self.setIntangibility(true);
            };
        }

        internal function frame3():*
        {
            this.self.playSound("bm_doublejump");
        }

        internal function frame10():*
        {
            this.self.playSound("run_start");
        }

        internal function frame11():*
        {
            this.self.setXSpeed(8, false);
        }

        internal function frame12():*
        {
            this.self.playAttackSound(1);
            this.self.attachEffect("global_dust_light");
        }

        internal function frame13():*
        {
            this.self.setIntangibility(false);
        }

        internal function frame25():*
        {
            this.self.endAttack();
        }


    }
}

