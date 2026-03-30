package dedede_fla
{
    import flash.display.MovieClip;

    public dynamic class Win_30 extends MovieClip
    {

        public var self:DededeExt;

        public function Win_30()
        {
            super();
            addFrameScript(0, this.frame1, 40, this.frame41, 53, this.frame54, 66, this.frame67, 116, this.frame117);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as DededeExt);
        }

        internal function frame41():*
        {
            SSF2API.playSound("ssf2_snd_sfx_dedede_uspec_longfail_01");
        }

        internal function frame54():*
        {
            SSF2API.playSound("ssf2_snd_sfx_dedede_uspec_longfail_01");
        }

        internal function frame67():*
        {
            SSF2API.playSound("ssf2_snd_sfx_dedede_uspec_longfail_01");
        }

        internal function frame117():*
        {
            this.gotoAndPlay("loop");
        }


    }
}

