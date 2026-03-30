package bandanadee_fla
{
    import flash.display.MovieClip;

    public dynamic class Skid_23 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var itemBox:MovieClip;
        public var self:BandanaDeeExt;
        public var fatland:Boolean;

        public function Skid_23()
        {
            super();
            addFrameScript(0, this.frame1, 6, this.frame7);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BandanaDeeExt);
            this.fatland = false;
            if (parent && SSF2API.isReady() && this.self)
            {
                this.self.setGlobalVariable("kirbyPeachUsed", false);
                this.self.playSound("bandanadee_dashstop");
            };
        }

        internal function frame7():*
        {
            this.self.endAttack();
        }


    }
}

