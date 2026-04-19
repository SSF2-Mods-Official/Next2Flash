// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.warp_141

package blackmage_fla
{
    import flash.display.MovieClip;

    public dynamic class warp_141 extends MovieClip 
    {

        internal var self:*;
        internal var xframe:String;
        internal var character:*;

        public function warp_141()
        {
            addFrameScript(0, this.frame1, 32, this.frame33, 43, this.frame44);
        }

        public function projDestroy(_arg_1:*):*
        {
            SSF2API.print("activated");
            this.character.removeEventListener(SSF2Event.CHAR_HURT, this.projDestroy);
            this.self.removeFromCamera();
            this.self.destroy();
        }

        internal function frame1():*
        {
            var _local_1:*;
            var _local_2:String;
            var _local_3:*;
            this.self = SSF2API.getProjectile(this);
            this.xframe = "charging";
            if (((SSF2API.isReady()) && (this.self)))
            {
                this.character = this.self.getOwner();
                this.self.addToCamera();
                this.character.addEventListener(SSF2Event.CHAR_HURT, this.projDestroy);
            };
        }

        internal function frame33():*
        {
            this.self.stancePlayFrame("charging");
        }

        internal function frame44():*
        {
            this.self.destroy();
        }


    }
}//package blackmage_fla

