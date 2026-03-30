package bandanadee_fla
{
    import flash.display.MovieClip;

    public dynamic class Get_UpRoll_109 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var itemBox:MovieClip;
        public var self:BandanaDeeExt;

        public function Get_UpRoll_109()
        {
            super();
            addFrameScript(0, this.frame1, 13, this.frame14, 22, this.frame23);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BandanaDeeExt);
            if (SSF2API.isReady() && this.self)
            {
                this.self.setIntangibility(true);
            };
        }

        internal function frame14():*
        {
            this.self.setIntangibility(false);
        }

        internal function frame23():*
        {
            this.self.endAttack();
        }


    }
}

