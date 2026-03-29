package captainfalcon_fla
{
    import flash.display.MovieClip;

    public dynamic class SpotDodge_161 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBoxw:MovieClip;
        public var itemBox:MovieClip;
        public var self:CaptainExt;

        public function SpotDodge_161()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 10, this.frame11, 14, this.frame15);
        }

        internal function frame1():*
        {
            if (SSF2API.isReady())
            {
                this.self = (SSF2API.getCharacter(this) as CaptainExt);
            };
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

        internal function frame15():*
        {
            this.self.endAttack();
        }


    }
}

