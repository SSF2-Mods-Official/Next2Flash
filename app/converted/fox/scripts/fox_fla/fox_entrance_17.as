package fox_fla
{
    import flash.display.MovieClip;

    public dynamic class fox_entrance_17 extends MovieClip
    {

        public var self:FoxExt;

        public function fox_entrance_17()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 12, this.frame13, 30, this.frame31);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as FoxExt);
        }

        internal function frame2():*
        {
            this.self.playSound("starFox_Entrance_sfx");
        }

        internal function frame13():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_l");
                SSF2API.getCamera().shake(3);
            }
            else
            {
                this.self.playSound("fox_landHeavy");
            };
            this.self.attachEffect("effect_land");
        }

        internal function frame31():*
        {
            SSF2API.getCharacter(this).endAttack();
        }


    }
}

