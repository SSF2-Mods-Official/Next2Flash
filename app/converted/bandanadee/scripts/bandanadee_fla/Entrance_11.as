package bandanadee_fla
{
    import flash.display.MovieClip;

    public dynamic class Entrance_11 extends MovieClip
    {

        public var self:BandanaDeeExt;

        public function Entrance_11()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 34, this.frame35, 36, this.frame37, 39, this.frame40);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BandanaDeeExt);
        }

        internal function frame2():*
        {
            SSF2API.playSound("bandanadee_entrance");
        }

        internal function frame35():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_s");
            }
            else
            {
                this.self.playSound("bandanadee_land1");
            };
        }

        internal function frame37():*
        {
            SSF2API.playSound("bandanadee_dashstart");
        }

        internal function frame40():*
        {
            SSF2API.getCharacter(this).endAttack();
        }


    }
}

