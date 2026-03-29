package captainfalcon_fla
{
    import flash.display.MovieClip;

    public dynamic class Get_UpAttack_175 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var hitBox6:MovieClip;
        public var itemBox:MovieClip;
        public var self:CaptainExt;

        public function Get_UpAttack_175()
        {
            super();
            addFrameScript(0, this.frame1, 4, this.frame5, 7, this.frame8, 10, this.frame11, 11, this.frame12, 12, this.frame13, 24, this.frame25);
        }

        internal function frame1():*
        {
            if (SSF2API.isReady())
            {
                this.self = (SSF2API.getCharacter(this) as CaptainExt);
                this.self.setIntangibility(true);
            };
        }

        internal function frame5():*
        {
            this.self.attachEffect("global_dust_swirl");
        }

        internal function frame8():*
        {
            this.self.playAttackSound(1);
            this.self.attachEffect("global_dust_swirl");
        }

        internal function frame11():*
        {
            this.self.refreshAttackID();
        }

        internal function frame12():*
        {
            this.self.playAttackSound(1);
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

