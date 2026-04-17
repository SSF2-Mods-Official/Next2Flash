// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//fox_fla.fox_staunt_135

package fox_fla
{
    import flash.display.MovieClip;

    public dynamic class fox_staunt_135 extends MovieClip 
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var itemBox:MovieClip;
        public var self:FoxExt;

        public function fox_staunt_135()
        {
            addFrameScript(0, this.frame1, 6, this.frame7, 7, this.frame8, 26, this.frame27, 27, this.frame28, 33, this.frame34, 40, this.frame41, 47, this.frame48, 56, this.frame57, 59, this.frame60, 67, this.frame68);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as FoxExt);
            if ((((parent) && (SSF2API.isReady())) && (this.self)))
            {
                if ((((this.self.isCPU()) && (this.self.getCPULevel() >= 8)) && (SSF2API.random() >= 0.5)))
                {
                    this.self.stancePlayFrame("CPUTaunt");
                };
            };
        }

        internal function frame7():*
        {
            this.self.addEffectToList(this.self.attachEffect("foxTauntEffect", {"parentLock":true}));
            this.self.clearEffectsOnStateChange();
        }

        internal function frame8():*
        {
            if (!this.self.getMetalStatus())
            {
                this.self.playSound("fox_taunt", true);
            };
            this.self.playSound("fox_uspecCharge");
        }

        internal function frame27():*
        {
            this.self.endAttack();
        }

        internal function frame28():*
        {
            this.self.importCPUControls([128, 2, 5441, 2, 128, 2, 5697, 2, 128, 2, 5441, 2, 128, 2, 5697, 2, 128, 2, 5441, 2, 128, 2, 5697, 2, 128, 2, 5441, 2, 128, 2, 5697, 2, 128, 2, 5441, 2, 128, 2, 5697, 2, 128, 2, 5441, 2, 128, 2, 5697, 1]);
        }

        internal function frame34():*
        {
            this.self.playSound("fox_gunflip");
        }

        internal function frame41():*
        {
            this.self.playSound("fox_gunflip");
        }

        internal function frame48():*
        {
            this.self.playSound("fox_gunflip");
        }

        internal function frame57():*
        {
            this.self.playSound("fox_gunflip");
        }

        internal function frame60():*
        {
            this.self.playSound("fox_nspec_end");
        }

        internal function frame68():*
        {
            this.self.endAttack();
        }


    }
}//package fox_fla

