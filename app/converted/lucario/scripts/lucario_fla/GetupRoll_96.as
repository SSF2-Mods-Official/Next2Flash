package lucario_fla
{
    import flash.display.MovieClip;

    public dynamic class GetupRoll_96 extends MovieClip
    {

        public var aura1:MovieClip;
        public var aura2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:LucarioExt;

        public function GetupRoll_96()
        {
            super();
            addFrameScript(0, this.frame1, 10, this.frame11, 11, this.frame12, 18, this.frame19);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as LucarioExt);
            if (SSF2API.isReady() && this.self)
            {
                this.self.setIntangibility(true);
                this.self.updateAuraPaws();
            };
        }

        internal function frame11():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame12():*
        {
            this.self.setIntangibility(false);
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_m");
            }
            else
            {
                this.self.playSound("lucario_land1");
            };
        }

        internal function frame19():*
        {
            this.self.endAttack();
        }


    }
}

