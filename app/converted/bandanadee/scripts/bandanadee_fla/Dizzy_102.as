package bandanadee_fla
{
    import flash.display.MovieClip;

    public dynamic class Dizzy_102 extends MovieClip
    {

        public var dizzy_stars:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BandanaDeeExt;

        public function Dizzy_102()
        {
            super();
            addFrameScript(0, this.frame1, 34, this.frame35);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BandanaDeeExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.self.playSound("ssf2_snd_vfx_bdee_hurtbad01");
            };
        }

        internal function frame35():*
        {
            this.self.stancePlayFrame("again");
        }


    }
}

