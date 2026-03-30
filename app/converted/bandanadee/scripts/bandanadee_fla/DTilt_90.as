package bandanadee_fla
{
    import flash.display.MovieClip;

    public dynamic class DTilt_90 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BandanaDeeExt;

        public function DTilt_90()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 2, this.frame3, 8, this.frame9, 15, this.frame16);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BandanaDeeExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.self.playAttackSound(1);
            };
        }

        internal function frame2():*
        {
            this.self.attachEffect("global_dust_light");
        }

        internal function frame3():*
        {
            this.self.setXSpeed(13.75, false);
        }

        internal function frame9():*
        {
            this.self.setXSpeed((this.self.getXSpeed() * 0.7));
        }

        internal function frame16():*
        {
            this.self.endAttack();
        }


    }
}

