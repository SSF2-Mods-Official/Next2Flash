// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//fox_fla.Fox_Hanggetup_115

package fox_fla
{
    import flash.display.MovieClip;

    public dynamic class Fox_Hanggetup_115 extends MovieClip 
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var itemBox:MovieClip;
        public var self:FoxExt;

        public function Fox_Hanggetup_115()
        {
            addFrameScript(0, this.frame1, 4, this.frame5, 7, this.frame8, 13, this.frame14, 15, this.frame16, 16, this.frame17);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as FoxExt);
            if (((SSF2API.isReady()) && (this.self)))
            {
                this.self.setIntangibility(true);
            };
        }

        internal function frame5():*
        {
            this.self.playSound("fox_jump01");
        }

        internal function frame8():*
        {
            this.self.setXSpeed(6, false);
        }

        internal function frame14():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_s2");
            }
            else
            {
                this.self.playSound("fox_footstep2");
            };
        }

        internal function frame16():*
        {
            this.self.setIntangibility(false);
        }

        internal function frame17():*
        {
            this.self.endAttack();
        }


    }
}//package fox_fla

