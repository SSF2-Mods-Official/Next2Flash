package bandanadee_fla
{
    import flash.display.MovieClip;

    public dynamic class SpotDodge_95 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:BandanaDeeExt;

        public function SpotDodge_95()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 10, this.frame11, 15, this.frame16);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BandanaDeeExt);
        }

        internal function frame2():*
        {
            this.self.setIntangibility(true);
            this.self.attachEffect("global_dust_cloud", {
                "scaleX":0.8,
                "scaleY":0.8
            });
        }

        internal function frame11():*
        {
            this.self.setIntangibility(false);
        }

        internal function frame16():*
        {
            this.self.endAttack();
        }


    }
}

