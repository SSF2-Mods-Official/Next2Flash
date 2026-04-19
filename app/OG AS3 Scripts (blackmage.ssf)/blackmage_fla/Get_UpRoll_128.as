// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.Get_UpRoll_128

package blackmage_fla
{
    import flash.display.MovieClip;

    public dynamic class Get_UpRoll_128 extends MovieClip 
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;

        public function Get_UpRoll_128()
        {
            addFrameScript(0, this.frame1, 10, this.frame11, 17, this.frame18);
        }

        internal function frame1():*
        {
            if (SSF2API.isReady())
            {
                this.self = (SSF2API.getCharacter(this) as BlackMageExt);
            };
            if (((parent) && (SSF2API.isReady())))
            {
                this.self.setIntangibility(true);
            };
        }

        internal function frame11():*
        {
            this.self.setIntangibility(false);
        }

        internal function frame18():*
        {
            this.self.endAttack();
        }


    }
}//package blackmage_fla

