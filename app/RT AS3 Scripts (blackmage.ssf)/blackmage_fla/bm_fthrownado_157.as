// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.bm_fthrownado_157

package blackmage_fla
{
    import flash.display.MovieClip;

    public dynamic class bm_fthrownado_157 extends MovieClip 
    {

        internal var self:*;
        internal var character:*;

        public function bm_fthrownado_157()
        {
            addFrameScript(0, this.frame1, 22, this.frame23);
        }

        public function remove(_arg_1:*):void
        {
            this.self.destroy();
            this.character.removeEventListener(SSF2Event.CHAR_HURT, this.remove);
        }

        internal function frame1():*
        {
            var _local_1:*;
            var _local_2:*;
            this.self = SSF2API.getProjectile(this);
            if (((SSF2API.isReady()) && (this.self)))
            {
                this.character = this.self.getOwner();
                this.character.addEventListener(SSF2Event.CHAR_HURT, this.remove);
            };
        }

        internal function frame23():*
        {
            this.self.destroy();
        }


    }
}//package blackmage_fla

